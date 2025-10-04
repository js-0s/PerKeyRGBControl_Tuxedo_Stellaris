"""
Constants for keyboard layout and localization.

This module defines the keyboard key numbering scheme (nom), ISO key names (key_names),
and localized key labels for different languages (localized_names).
"""

from __future__ import annotations

from .key_names import key_names
from .localized_names import localized_names

__all__ = ["nom", "key_names", "localized_names"]

# These are the corresponding numbers to the different keys on the keyboard
nom: list[list[int]] = [
    [
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        122,
        123,
        124,
    ],
    [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 98, 98, 98, 99, 100, 101, 102],
    [63, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 77, 77, 78, 79, 80, 81],
    [42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 77, 77, 77, 57, 58, 59, 81],
    [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 125, 35, 35, 35, 36, 37, 38, 39],
    [-1, 2, 3, 4, 7, 7, 7, 7, 7, 7, 10, 12, 12, 118, 14, 120, 16, 16, 17, 39],
    [
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        125,
        13,
        18,
        15,
        125,
        125,
        125,
        125,
    ],
]
