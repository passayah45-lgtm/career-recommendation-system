# Recovers a page when part of the Streamlit frontend fails to download
# Seen on iPhone Safari as "TypeError: Importing a module script failed." in place of every input widget:
# one shared JavaScript file did not arrive (network drop, app restart during a deploy or wake-up), and the
# browser keeps that failure until the page is reloaded. Streamlit announces such failures with the standard
# vite:preloadError event but does not handle it, so the app listens for it here. A failure can also happen before
# this script itself has loaded; the error boxes Streamlit shows for it are then found on the page instead.
# WebKit (iPhone Safari and iPhone Chrome) keeps serving the failed file even after a normal reload, a new visit or
# a new query string (tested with WebKitGTK 2.52 on 4 November 2026). Downloading the page's preloaded module files
# again with the browser cache bypassed, then reloading, is what replaces it, so every reload here does that first.
# Display only: nothing here touches answers, scoring or the saved session format.

# A second failure within this many seconds of an automatic reload shows the message instead of reloading again
RELOAD_GUARD_SECONDS = 30
# Seconds after the script starts at which the page is checked for failures that happened before it loaded
SCAN_DELAYS = (0, 1.5, 5)
# The browser's own wording inside Streamlit's error box, in Safari, Chrome and Firefox
FAILURE_PATTERN = (r"TypeError:?\s*(Importing a module script failed|Failed to fetch dynamically imported module|"
                   r"error loading dynamically imported module)")
NOTICE_ID = "crs-load-notice"
# Keyed container around the script; styles.css hides it so it takes no space
RECOVERY_KEY = "load_recovery"
RELOAD_KEY = "crs-chunk-reload-at"

NOTICE_TEXT = "Part of this page did not load, so some fields are missing. Reload the page to fix it."
NOTICE_TEXT_WITH_DATA = ("Part of this page did not load, so some fields are missing. Reloading clears the answers "
                         "kept in this browser session. To keep them, open Your session data and download the file, "
                         "then reload the page and upload it again.")
RELOAD_LABEL = "Reload the page"
RELOADING_LABEL = "Reloading..."
# The page reloads after this many seconds even if downloading the files again has not finished
REFRESH_TIMEOUT_SECONDS = 8

_SCRIPT = """<script>
(function () {
  window.__crsHasSessionData = %(has_data)s;
  if (window.__crsChunkRecovery) { return; }
  window.__crsChunkRecovery = true;
  var handled = false;
  var failure = new RegExp(%(pattern)s, "i");
  function showNotice() {
    if (document.getElementById("%(notice_id)s")) { return; }
    var box = document.createElement("div");
    box.id = "%(notice_id)s";
    box.setAttribute("role", "alert");
    // Near the top, below the app header, so hosting badges in the bottom corner never cover it
    box.style.cssText = "position:fixed;left:12px;right:12px;top:68px;z-index:100000;max-width:640px;" +
      "margin:0 auto;padding:12px 14px;border-radius:10px;background:#FDF0E6;color:#9A3412;" +
      "border:1px solid #C2410C;font:15px/1.4 'Source Sans Pro',sans-serif;box-shadow:0 4px 14px rgba(0,0,0,.12)";
    var text = document.createElement("div");
    text.textContent = window.__crsHasSessionData ? %(text_with_data)s : %(text)s;
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = %(label)s;
    button.style.cssText = "margin-top:8px;min-height:44px;padding:8px 14px;border-radius:8px;border:0;" +
      "background:#0B7F78;color:#FFFFFF;font:inherit;cursor:pointer";
    button.addEventListener("click", function () {
      button.disabled = true;
      button.textContent = %(reloading)s;
      reloadPage();
    });
    box.appendChild(text);
    box.appendChild(button);
    document.body.appendChild(box);
  }
  function reloadPage() {
    // Downloads the module files again without the browser cache, so WebKit forgets the failed copy, then reloads
    var links = document.querySelectorAll('link[rel="modulepreload"]');
    var jobs = [];
    for (var i = 0; i < links.length; i++) {
      jobs.push(fetch(links[i].href, { cache: "reload", credentials: "same-origin" })
        .catch(function () { return null; }));
    }
    var limit = new Promise(function (done) { setTimeout(done, %(refresh_ms)d); });
    Promise.race([Promise.all(jobs), limit]).then(function () { window.location.reload(); });
  }
  function handleFailure() {
    // One response per page load, however many widget files fail at the same time
    if (handled) { return; }
    handled = true;
    // Answers live only in this browser session, so the page never reloads by itself once there are any
    if (window.__crsHasSessionData) { showNotice(); return; }
    var now = Date.now(), last = 0;
    try { last = Number(window.sessionStorage.getItem("%(reload_key)s")) || 0; } catch (e) { showNotice(); return; }
    if (now - last < %(guard_ms)d) { showNotice(); return; }
    try { window.sessionStorage.setItem("%(reload_key)s", String(now)); } catch (e) { showNotice(); return; }
    reloadPage();
  }
  function scan() {
    var boxes = document.querySelectorAll('[data-testid="stAlertContentError"]');
    for (var i = 0; i < boxes.length; i++) {
      if (failure.test(boxes[i].textContent)) { handleFailure(); return; }
    }
  }
  window.addEventListener("vite:preloadError", handleFailure);
  %(scans)s
})();
</script>"""


def _js_string(text):
    # A JavaScript string literal for fixed app text; no student input is ever passed here
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def recovery_script(has_session_data):
    return _SCRIPT % {
        "has_data": "true" if has_session_data else "false",
        "notice_id": NOTICE_ID,
        "reload_key": RELOAD_KEY,
        "guard_ms": RELOAD_GUARD_SECONDS * 1000,
        "text": _js_string(NOTICE_TEXT),
        "text_with_data": _js_string(NOTICE_TEXT_WITH_DATA),
        "label": _js_string(RELOAD_LABEL),
        "reloading": _js_string(RELOADING_LABEL),
        "refresh_ms": REFRESH_TIMEOUT_SECONDS * 1000,
        "pattern": _js_string(FAILURE_PATTERN),
        "scans": " ".join("scan();" if d == 0 else f"setTimeout(scan, {int(d * 1000)});" for d in SCAN_DELAYS),
    }
