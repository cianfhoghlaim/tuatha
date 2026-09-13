"""tuatha.theming.color — colour space maths for the ANAM palette work.

Perceptual distance is the unit the ANAM pipeline reasons in. A derived
ANAM colour is allowed to drift from its source toward the turquoise/blue
palette, but only so far — and "so far" has to mean something to an eye,
not to an RGB triple. Two colours 30 apart in RGB can be
indistinguishable or obviously different depending on where they sit, so
comparisons go through CIE-Lab.

This lived in ``tuatha/notebooks/anam/helpers``. Production code should
not import from a notebook, and the ANAM quality gate needs it.
"""

from __future__ import annotations

import re

__all__ = [
    "DELTA_E_JND",
    "DELTA_E_PERCEPTIBLE",
    "delta_e",
    "hex_to_rgb",
    "is_valid_hex",
    "rgb_to_lab",
]

_HEX = re.compile(r"^#?[0-9a-fA-F]{6}$")

#: ΔE below which a difference is imperceptible even side by side.
DELTA_E_JND = 1.0

#: ΔE below which a difference is perceptible only on close inspection.
#: The ANAM gate's default threshold sits above this: the derived colour
#: is meant to be recognisably related to its source, not identical.
DELTA_E_PERCEPTIBLE = 2.0


def is_valid_hex(value: str) -> bool:
    """Return whether ``value`` is a ``#RRGGBB`` colour."""
    return bool(_HEX.match(value or ""))


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Parse ``#RRGGBB`` into an 8-bit RGB triple.

    Raises:
        ValueError: on anything that is not six hex digits. Silently
            returning black would make a malformed colour look like a
            deliberate one, and the ANAM gate would score it.
    """
    if not is_valid_hex(hex_color):
        raise ValueError(
            f"{hex_color!r} is not a #RRGGBB colour; the ANAM pipeline "
            "stores colours in that form only"
        )
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert 8-bit sRGB to CIE-Lab under a D65 illuminant."""
    r, g, b = (c / 255.0 for c in rgb)

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    rl, gl, bl = lin(r), lin(g), lin(b)

    # linear sRGB -> XYZ, normalised to the D65 white point
    x = (rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375) / 0.95047
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = (rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041) / 1.08883

    def f(t: float) -> float:
        return t ** (1.0 / 3.0) if t > 0.008856 else (7.787 * t) + (16.0 / 116.0)

    lightness = 116.0 * f(y) - 16.0
    a_star = 500.0 * (f(x) - f(y))
    b_star = 200.0 * (f(y) - f(z))
    return lightness, a_star, b_star


def delta_e(c1: str, c2: str) -> float:
    """CIE76 ΔE between two ``#RRGGBB`` colours.

    CIE76 is the simplest of the ΔE formulas and overstates differences
    in saturated blues — which is exactly where the ANAM turquoise
    palette sits. It is kept because the threshold was calibrated
    against it; moving to CIEDE2000 would require recalibrating.
    """
    l1, a1, b1 = rgb_to_lab(hex_to_rgb(c1))
    l2, a2, b2 = rgb_to_lab(hex_to_rgb(c2))
    return ((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5
