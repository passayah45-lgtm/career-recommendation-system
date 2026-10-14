# HTTP checker for resource and career source URLs
# Needs internet access. Never runs in CI or the normal test suite.
# Run: python -m src.data.url_checker --output reports/url_check.json
# Apply reachable results to resources.csv (keeps the earlier status in notes): add --apply

import argparse
import csv
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from src.data.validation import CAREERS_FILE, DEFAULT_DATA_DIR, RESOURCE_COLUMNS, RESOURCES_FILE, read_csv

USER_AGENT = "CareerRecommendationSystem-LinkChecker/1.0 (academic project; polite single-thread checks)"
DEFAULT_TIMEOUT = 15
DEFAULT_HOST_DELAY = 1.5
MAX_RETRY_AFTER = 30

REACHABLE = "reachable"
FAILED = "failed"
BLOCKED = "blocked"
INCONCLUSIVE = "inconclusive"
OUTCOMES = (REACHABLE, FAILED, BLOCKED, INCONCLUSIVE)

# 404 and 410 are the only codes treated as evidence that a page is gone
FAILED_CODES = {404, 410}
# Access refused or rate limited: the page may exist, so these never count as failed
BLOCKED_CODES = {401, 403, 429, 451, 999}
# HEAD is retried with GET for these, because many servers mishandle HEAD
GET_FALLBACK_CODES = {400, 403, 404, 405, 406, 429, 500, 501, 502, 503}


@dataclass
class CheckResult:
    record_type: str
    record_id: str
    url: str
    outcome: str
    status_code: object = None
    final_url: object = None
    redirected: bool = False
    method: str = ""
    error: str = ""
    checked_at: str = ""


@dataclass
class HttpResponse:
    status: int
    final_url: str
    headers: dict


class HttpError(Exception):
    # Raised by the transport for non-2xx/3xx responses
    def __init__(self, status, final_url, headers=None):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.final_url = final_url
        self.headers = headers or {}


def urllib_transport(url, method, timeout):
    # Real network call. Redirects are followed by urllib. Body is not downloaded beyond the first bytes.
    request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            if method == "GET":
                resp.read(1024)
            return HttpResponse(resp.status, resp.geturl(), dict(resp.headers))
    except urllib.error.HTTPError as exc:
        raise HttpError(exc.code, exc.geturl() or url, dict(exc.headers or {})) from exc


def classify_status(code):
    if 200 <= code < 400:
        return REACHABLE
    if code in FAILED_CODES:
        return FAILED
    if code in BLOCKED_CODES:
        return BLOCKED
    return INCONCLUSIVE


def _retry_after_seconds(headers):
    value = (headers or {}).get("Retry-After") or (headers or {}).get("retry-after")
    try:
        return max(0, min(MAX_RETRY_AFTER, int(value)))
    except (TypeError, ValueError):
        return None


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def check_url(url, record_type="", record_id="", transport=urllib_transport, timeout=DEFAULT_TIMEOUT,
              sleep=time.sleep, clock=_now):
    # Checks one URL: HEAD first, GET fallback, one polite retry after a 429 with Retry-After
    result = CheckResult(record_type, record_id, url, INCONCLUSIVE, checked_at=clock())
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        result.error = "not an http(s) URL"
        return result

    attempts = [("HEAD", False), ("GET", False)]
    last_status = None
    for method, retried in attempts:
        try:
            resp = transport(url, method, timeout)
        except HttpError as exc:
            last_status = exc.status
            result.status_code, result.final_url, result.method = exc.status, exc.final_url, method
            result.outcome = classify_status(exc.status)
            result.error = f"HTTP {exc.status}"
            wait = _retry_after_seconds(exc.headers) if exc.status == 429 else None
            if wait is not None and not retried:
                sleep(wait)
                attempts.append((method, True))
                continue
            if method == "HEAD" and exc.status in GET_FALLBACK_CODES:
                continue
            break
        except ssl.SSLError as exc:
            result.outcome, result.method, result.error = INCONCLUSIVE, method, f"TLS error: {exc}"
            break
        except (socket.timeout, TimeoutError) as exc:
            result.outcome, result.method, result.error = INCONCLUSIVE, method, f"timeout: {exc}"
            break
        except (urllib.error.URLError, ConnectionError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, ssl.SSLError):
                result.error = f"TLS error: {reason}"
            elif isinstance(reason, (socket.timeout, TimeoutError)):
                result.error = f"timeout: {reason}"
            else:
                result.error = f"connection error: {reason}"
            result.outcome, result.method = INCONCLUSIVE, method
            break
        else:
            result.status_code, result.final_url, result.method = resp.status, resp.final_url, method
            result.outcome = classify_status(resp.status)
            result.error = ""
            break
    if result.final_url and result.final_url != url:
        result.redirected = True
    if result.outcome != REACHABLE and last_status is None and not result.error:
        result.error = "no response"
    return result


def collect_targets(data_dir=DEFAULT_DATA_DIR):
    # Every resource URL and every non-empty career source URL, in file order
    data_dir = Path(data_dir)
    resources, _ = read_csv(data_dir / RESOURCES_FILE)
    careers, _ = read_csv(data_dir / CAREERS_FILE)
    targets = [("resource", r["resource_id"], r["resource_url"]) for r in resources]
    targets += [("career_source", c["career_id"], c["source_url"]) for c in careers if c["source_url"]]
    return targets


def check_all(targets, transport=urllib_transport, timeout=DEFAULT_TIMEOUT, host_delay=DEFAULT_HOST_DELAY,
              sleep=time.sleep, clock=_now, monotonic=time.monotonic, progress=None):
    # Sequential checks with a minimum delay between requests to the same host
    last_hit = {}
    results = []
    for i, (record_type, record_id, url) in enumerate(targets, start=1):
        host = urlparse(url).netloc
        if host in last_hit:
            wait = host_delay - (monotonic() - last_hit[host])
            if wait > 0:
                sleep(wait)
        results.append(check_url(url, record_type, record_id, transport, timeout, sleep, clock))
        last_hit[host] = monotonic()
        if progress:
            progress(i, len(targets), results[-1])
    return results


def summarize(results):
    counts = {o: 0 for o in OUTCOMES}
    for r in results:
        counts[r.outcome] += 1
    return {"total": len(results), "outcomes": counts,
            "redirected": sum(1 for r in results if r.redirected)}


def build_report(results):
    return {
        "generated_at": _now(),
        "meaning": {
            REACHABLE: "Server returned a 2xx or 3xx response (after following redirects).",
            FAILED: "Server returned 404 or 410: the page is likely gone.",
            BLOCKED: "Server refused or rate-limited the checker (401, 403, 429, 451, 999). The page may still exist.",
            INCONCLUSIVE: "Timeout, TLS or connection error, 5xx or another code. Nothing was established.",
        },
        "summary": summarize(results),
        "results": [asdict(r) for r in results],
    }


def apply_to_resources(results, resources_path, date_str):
    # Marks only reachable resource URLs as http_checked and keeps the earlier status in notes
    reachable = {r.record_id for r in results if r.record_type == "resource" and r.outcome == REACHABLE}
    rows, columns = read_csv(resources_path)
    changed = 0
    for row in rows:
        if row["resource_id"] not in reachable or row["url_verification"] == "http_checked":
            continue
        earlier = f"Earlier status: {row['url_verification']} on {row['verified_on'] or 'unknown date'}."
        row["notes"] = f"{row['notes']} {earlier}".strip() if row["notes"] else earlier
        row["url_verification"] = "http_checked"
        row["verified_on"] = date_str
        changed += 1
    with open(resources_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns or RESOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check resource and career source URLs over HTTP.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output", default="reports/url_check.json")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--delay", type=float, default=DEFAULT_HOST_DELAY, help="seconds between requests to one host")
    parser.add_argument("--apply", action="store_true", help="mark reachable resources as http_checked in resources.csv")
    args = parser.parse_args(argv)

    targets = collect_targets(args.data_dir)
    print(f"Checking {len(targets)} URLs one at a time. This takes a few minutes.")

    def progress(i, n, r):
        print(f"[{i}/{n}] {r.outcome:<12} {r.status_code or '-':<4} {r.url}")

    results = check_all(targets, timeout=args.timeout, host_delay=args.delay, progress=progress)
    report = build_report(results)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to {args.output}")
    if args.apply:
        changed = apply_to_resources(results, Path(args.data_dir) / RESOURCES_FILE,
                                     datetime.now(timezone.utc).date().isoformat())
        print(f"Updated {changed} resource rows to http_checked. Run python -m src.data.validation next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
