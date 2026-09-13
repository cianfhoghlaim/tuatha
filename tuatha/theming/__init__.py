"""tuatha.theming — palette and colour handling for the game surface.

Currently the colour-space maths the ANAM quality gate measures with.
The provenance-anchored palette layer (the G10 gate: every palette must
resolve to a fetched source document) lands here next.
"""

from .color import (
    DELTA_E_JND,
    DELTA_E_PERCEPTIBLE,
    delta_e,
    hex_to_rgb,
    is_valid_hex,
    rgb_to_lab,
)

__all__ = [
    "DELTA_E_JND",
    "DELTA_E_PERCEPTIBLE",
    "delta_e",
    "hex_to_rgb",
    "is_valid_hex",
    "rgb_to_lab",
]
