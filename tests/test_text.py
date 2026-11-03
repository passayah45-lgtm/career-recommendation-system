# Text a student typed is shown as plain characters: no Markdown link, image, HTML or Streamlit directive is built

import re
import string

import pytest

from src.ui.text import ZERO_WIDTH_SPACE, escape_typed, plain_markdown

TRICKY = [
    "![x](https://example.com/t.png) [link](https://example.com)",
    "<img src=https://example.com/t.png onerror=alert(1)>",
    "<script>alert(1)</script> <b>bold</b> &lt;",
    "**bold** _italic_ `code` ~~gone~~ $x^2$",
    ":red[colour] :material/home: :smile:",
    "# heading\n- list item\n> quote",
    "https://example.com www.example.com me@example.net",
]
# The patterns Streamlit's Markdown uses to turn bare web and email addresses into links
AUTOLINK = re.compile(r"(https?://|www\.)|([-.\w+]+@[-\w]+(\.[-\w]+)+)", re.I)


def _readable(shown):
    # What the student sees: escapes removed and the invisible zero-width spaces dropped
    return re.sub(r"\\(.)", r"\1", shown).replace(ZERO_WIDTH_SPACE, "")


def _unescaped_punctuation(text):
    # Punctuation not preceded by a backslash; after escaping there must be none
    return [m.group(0) for m in re.finditer(r"(?<!\\)[" + re.escape(string.punctuation.replace("\\", "")) + "]", text)]


@pytest.mark.parametrize("raw", TRICKY)
def test_every_markdown_or_html_character_is_escaped(raw):
    shown = plain_markdown(raw)
    assert _unescaped_punctuation(shown) == []
    assert "\n" not in shown
    # Removing the escapes gives back the typed characters, so the text stays readable
    assert _readable(shown) == " ".join(raw.split())
    # Bare addresses can no longer be turned into links once the escapes are read
    assert not AUTOLINK.search(re.sub(r"\\(.)", r"\1", shown))


def test_ordinary_interests_are_unchanged():
    for raw in ("Agricultural development", "Community leadership", "Rural entrepreneurship", "Mine"):
        assert plain_markdown(raw) == raw


def test_only_typed_parts_of_a_warning_are_escaped():
    message = "These interests are not in the interest list and were not scored: [a](https://example.com), Mine."
    shown = escape_typed(message, ["[a](https://example.com)", "Mine"])
    assert shown.startswith("These interests are not in the interest list and were not scored: ")
    assert _readable(shown) == message and shown.endswith(", Mine.")
    assert "[a](" not in shown and not AUTOLINK.search(re.sub(r"\\(.)", r"\1", shown))
    assert escape_typed(message, []) == message


def test_overlapping_typed_parts_are_escaped_once():
    shown = escape_typed("x: a.b, a.b.c.", ["a.b", "a.b.c"])
    z = ZERO_WIDTH_SPACE
    assert shown == f"x: a{z}\\.b, a{z}\\.b{z}\\.c."
