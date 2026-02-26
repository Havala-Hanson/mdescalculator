"""
MDES Engines – statistical computation modules for multilevel randomized trials.

Supported designs
-----------------
Two-level CRT   : CRA2_2  (mdes_two_level)
Three-level CRT : CRA3_3, BCRA3_2  (mdes_three_level)
Blocked two-level: BCRA2_2  (mdes_blocked)
"""

from .mdes_two_level import compute_mdes_cra2_2
from .mdes_three_level import compute_mdes_cra3_3, compute_mdes_bcra3_2
from .mdes_blocked import compute_mdes_bcra2_2

__all__ = [
    "compute_mdes_cra2_2",
    "compute_mdes_cra3_3",
    "compute_mdes_bcra3_2",
    "compute_mdes_bcra2_2",
]
