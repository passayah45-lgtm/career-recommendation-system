# Original inline SVG graphics: hero illustration, sidebar card art and progress rings
# Plain strings, no Streamlit import, so they can be tested on their own

from html import escape
from math import pi

from src.ui.theme import BLUE, NAVY, TEAL, TEAL_DARK

RING_TRACK = "#E6EBF2"

# Ascending steps with a flag and a rising path: career growth, drawn from basic shapes
HERO_SVG = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 210" width="320" height="210"
     role="img" aria-label="Rising steps with a flag at the top">
  <circle cx="250" cy="70" r="62" fill="#E3F4F2"/>
  <circle cx="70" cy="150" r="46" fill="#E6EEFD"/>
  <rect x="40" y="150" width="46" height="44" rx="6" fill="#7DD3C8"/>
  <rect x="96" y="122" width="46" height="72" rx="6" fill="{TEAL}"/>
  <rect x="152" y="94" width="46" height="100" rx="6" fill="{TEAL_DARK}"/>
  <rect x="208" y="62" width="46" height="132" rx="6" fill="{NAVY}"/>
  <path d="M60 140 C 110 120, 150 96, 228 50" fill="none" stroke="{BLUE}" stroke-width="3"
        stroke-dasharray="6 6" stroke-linecap="round"/>
  <line x1="231" y1="62" x2="231" y2="18" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>
  <path d="M233 19 L262 27 L233 36 Z" fill="#F97316"/>
  <rect x="20" y="194" width="280" height="4" rx="2" fill="#DCE3EC"/>
</svg>
"""

# Hills and a flag for the card at the bottom of the sidebar
SIDEBAR_ART = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 80" width="220" height="80" role="img"
     aria-label="Hills with a flag">
  <path d="M0 80 L60 30 L100 62 L150 18 L220 80 Z" fill="{TEAL}"/>
  <path d="M0 80 L45 52 L85 80 Z" fill="#7DD3C8"/>
  <path d="M110 80 L170 42 L220 70 L220 80 Z" fill="{TEAL_DARK}"/>
  <line x1="150" y1="18" x2="150" y2="0" stroke="#E2E8F0" stroke-width="2"/>
  <path d="M151 1 L166 5 L151 10 Z" fill="#F97316"/>
</svg>
"""


def ring_svg(fraction, center_text, size=64, stroke=7, color=TEAL, label=""):
    # Circular progress indicator, fraction between 0 and 1, always shown with a text value inside
    fraction = 0.0 if fraction is None else max(0.0, min(1.0, float(fraction)))
    radius = (size - stroke) / 2
    circumference = 2 * pi * radius
    filled = circumference * fraction
    half = size / 2
    font = max(11, round(size * 0.26))
    # No arc at zero, a rounded line end would otherwise draw a dot
    arc = (f'<circle cx="{half}" cy="{half}" r="{radius:.2f}" fill="none" stroke="{color}" stroke-width="{stroke}" '
           f'stroke-linecap="round" stroke-dasharray="{filled:.2f} {circumference:.2f}" '
           f'transform="rotate(-90 {half} {half})"/>') if filled > 0 else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" role="img" aria-label="{escape(label or center_text, quote=True)}">'
        f'<circle cx="{half}" cy="{half}" r="{radius:.2f}" fill="none" stroke="{RING_TRACK}" stroke-width="{stroke}"/>'
        f'{arc}'
        f'<text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" '
        f'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif" font-size="{font}" font-weight="700" '
        f'fill="{NAVY}">{escape(center_text)}</text></svg>'
    )


def initial_tile(text, color=BLUE):
    # Square tile with the first letter of a provider name, a neutral stand-in for a logo
    letter = escape((text or "?").strip()[:1].upper() or "?")
    return (f'<div style="width:40px;height:40px;border-radius:10px;background:{color};color:#FFFFFF;'
            f'display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem">'
            f'{letter}</div>')
