# Shows text a student typed exactly as typed inside Streamlit markdown, captions and alerts
# Display only: the saved value is never changed, only how it is drawn on the page

import re
import string

# Every ASCII punctuation mark can be escaped with a backslash in Markdown, which stops links, images, HTML,
# formatting and Streamlit directives such as :material/x: or :red[x] from being built out of typed text
_PUNCTUATION = re.compile("([" + re.escape(string.punctuation) + "])")
# Streamlit turns bare web and email addresses into links even after escaping, so an invisible zero-width space
# goes after every colon and before every dot and @: "https://", "www." and "name@site" can then never match
ZERO_WIDTH_SPACE = "​"
_BREAK_ADDRESSES = ((r"\:", r"\:" + ZERO_WIDTH_SPACE), (r"\.", ZERO_WIDTH_SPACE + r"\."),
                    (r"\@", ZERO_WIDTH_SPACE + r"\@"))


def plain_markdown(text):
    # Line breaks become spaces so typed text cannot start a heading, list or quote on a new line
    flat = " ".join(str(text).split())
    shown = _PUNCTUATION.sub(r"\\\1", flat)
    for old, new in _BREAK_ADDRESSES:
        shown = shown.replace(old, new)
    return shown


def escape_typed(message, typed):
    # Escapes only the typed parts inside a sentence the app wrote, longest first, in a single pass
    parts = sorted({str(t) for t in typed if str(t)}, key=len, reverse=True)
    if not parts:
        return message
    pattern = re.compile("|".join(re.escape(p) for p in parts))
    return pattern.sub(lambda m: plain_markdown(m.group(0)), message)
