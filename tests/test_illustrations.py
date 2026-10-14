# SVG graphics: rings show the right share, stay inside bounds, escape text and carry an accessible label

import re

import pytest

from src.ui.illustrations import HERO_SVG, SIDEBAR_ART, initial_tile, ring_svg


def arc_lengths(svg):
    match = re.search(r'stroke-dasharray="([\d.]+) ([\d.]+)"', svg)
    return (float(match.group(1)), float(match.group(2))) if match else None


@pytest.mark.parametrize("fraction", [0.25, 0.8, 1.0])
def test_ring_arc_matches_fraction(fraction):
    filled, total = arc_lengths(ring_svg(fraction, "x"))
    assert filled / total == pytest.approx(fraction, abs=0.001)


def test_ring_clamps_and_handles_missing_values():
    assert arc_lengths(ring_svg(1.7, "x"))[0] == pytest.approx(arc_lengths(ring_svg(1.0, "x"))[0])
    for value in (0, -0.3, None):
        assert arc_lengths(ring_svg(value, "x")) is None


def test_ring_text_and_label_are_escaped():
    svg = ring_svg(0.5, "<b>50%</b>", label='a "quoted" label')
    assert "<b>" not in svg and "&lt;b&gt;50%&lt;/b&gt;" in svg
    assert 'aria-label="a &quot;quoted&quot; label"' in svg


def test_graphics_are_standalone_svg_with_labels():
    for svg in (HERO_SVG, SIDEBAR_ART, ring_svg(0.4, "40%")):
        assert svg.strip().startswith("<svg") and 'xmlns="http://www.w3.org/2000/svg"' in svg
        assert 'role="img"' in svg and "aria-label=" in svg
        assert "http" not in svg.replace("http://www.w3.org/2000/svg", "")


def test_initial_tile_uses_first_letter_safely():
    assert ">K</div>" in initial_tile("kaggle")
    assert "&lt;" in initial_tile("<script>")
    assert ">?</div>" in initial_tile("")
