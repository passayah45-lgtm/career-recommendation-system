# URL checker logic with a mocked transport. No real network access.

import csv
import socket
import ssl
import urllib.error

import pytest

from src.data import url_checker as uc
from src.data.validation import RESOURCE_COLUMNS
from tests.conftest import resource_row, write_csv

CLOCK = lambda: "2026-10-14T00:00:00+00:00"  # noqa: E731


class FakeTransport:
    # Replays scripted responses per (method) call and records calls
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, url, method, timeout):
        self.calls.append(method)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        status, final = item
        if status >= 400:
            raise uc.HttpError(status, final, {})
        return uc.HttpResponse(status, final, {})


def check(script, url="https://example.org/a"):
    t = FakeTransport(script)
    return uc.check_url(url, "resource", "R001", transport=t, sleep=lambda s: None, clock=CLOCK), t.calls


def test_head_success_is_reachable():
    r, calls = check([(200, "https://example.org/a")])
    assert r.outcome == uc.REACHABLE and r.status_code == 200 and calls == ["HEAD"] and not r.redirected


def test_redirect_is_recorded():
    r, _ = check([(200, "https://example.org/new")])
    assert r.outcome == uc.REACHABLE and r.redirected and r.final_url == "https://example.org/new"


def test_head_not_allowed_falls_back_to_get():
    r, calls = check([(405, "https://example.org/a"), (200, "https://example.org/a")])
    assert r.outcome == uc.REACHABLE and r.method == "GET" and calls == ["HEAD", "GET"]


def test_404_after_get_is_failed():
    r, calls = check([(404, "https://example.org/a"), (404, "https://example.org/a")])
    assert r.outcome == uc.FAILED and r.status_code == 404 and calls == ["HEAD", "GET"]


@pytest.mark.parametrize("code", [401, 403, 429, 999])
def test_blocked_codes_are_never_failed(code):
    r, _ = check([(code, "u"), (code, "u")])
    assert r.outcome == uc.BLOCKED


def test_server_error_is_inconclusive():
    r, _ = check([(503, "u"), (503, "u")])
    assert r.outcome == uc.INCONCLUSIVE


@pytest.mark.parametrize("exc,text", [
    (socket.timeout("timed out"), "timeout"),
    (ssl.SSLError("bad cert"), "TLS"),
    (urllib.error.URLError("Name or service not known"), "connection"),
    (urllib.error.URLError(ssl.SSLError("handshake")), "TLS"),
])
def test_network_errors_are_inconclusive(exc, text):
    r, _ = check([exc])
    assert r.outcome == uc.INCONCLUSIVE and text in r.error and r.status_code is None


def test_rate_limit_retry_after_is_respected():
    slept = []

    class T(FakeTransport):
        def __call__(self, url, method, timeout):
            self.calls.append(method)
            item = self.script.pop(0)
            if item == 429:
                raise uc.HttpError(429, url, {"Retry-After": "3"})
            return uc.HttpResponse(200, url, {})

    t = T([429, 200])
    r = uc.check_url("https://example.org/a", transport=t, sleep=slept.append, clock=CLOCK)
    assert slept == [3] and r.outcome == uc.REACHABLE


def test_invalid_url_is_not_requested():
    r, calls = check([], url="ftp://example.org/a")
    assert r.outcome == uc.INCONCLUSIVE and calls == []


def test_check_all_is_sequential_with_host_delay():
    slept, times = [], iter([0.0, 0.2, 0.3, 5.0, 5.1])
    t = FakeTransport([(200, "u")] * 3)
    targets = [("resource", "R1", "https://a.org/1"), ("resource", "R2", "https://a.org/2"),
               ("resource", "R3", "https://b.org/1")]
    results = uc.check_all(targets, transport=t, host_delay=1.5, sleep=slept.append, clock=CLOCK,
                           monotonic=lambda: next(times))
    assert [r.record_id for r in results] == ["R1", "R2", "R3"]
    assert slept == [pytest.approx(1.3)]
    assert uc.summarize(results)["outcomes"][uc.REACHABLE] == 3


def test_collect_targets_reads_real_files():
    targets = uc.collect_targets()
    assert sum(1 for t in targets if t[0] == "resource") == 114
    assert sum(1 for t in targets if t[0] == "career_source") == 46


def test_apply_only_marks_reachable_and_keeps_earlier_status(tmp_path):
    path = write_csv(tmp_path / "resources.csv", RESOURCE_COLUMNS,
                     [resource_row(1, "python"), resource_row(2, "sql", notes="Free account needed")])
    results = [uc.CheckResult("resource", "R001", "u", uc.REACHABLE),
               uc.CheckResult("resource", "R002", "u", uc.BLOCKED)]
    assert uc.apply_to_resources(results, path, "2026-11-01") == 1
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    assert rows[0]["url_verification"] == "http_checked" and rows[0]["verified_on"] == "2026-11-01"
    assert "Earlier status: search_index_confirmed on 2026-10-14." in rows[0]["notes"]
    assert rows[1]["url_verification"] == "search_index_confirmed" and rows[1]["notes"] == "Free account needed"


def test_report_shape():
    report = uc.build_report([uc.CheckResult("resource", "R001", "u", uc.FAILED, 404)])
    assert report["summary"]["outcomes"][uc.FAILED] == 1
    assert set(report["results"][0]) >= {"url", "record_id", "status_code", "final_url", "checked_at", "outcome"}
