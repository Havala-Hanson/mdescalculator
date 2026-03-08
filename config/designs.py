from typing import NamedTuple, List, Dict, Optional

class DesignInfo(NamedTuple):
    code: str
    title: str
    description: str
    icon: str
    page: str

    # Core Dong & Maynard dimensions
    is_blocked: bool
    levels: int
    assignment_unit: str          # "individual", "cluster", "district", etc.
    assignment_level: int         # numeric level of assignment
    block_effect: Optional[str]   # "constant", "fixed", "random", None

    # Design family
    design_family: str            # "IRA", "BIRA", "CRA", "BCRA", "RD", "ITS"

    # Experimental vs quasi-experimental
    is_randomized: bool
    is_quasi_experimental: bool

    # Additional QED structure
    requires_cutoff: bool         # RD
    requires_pre_post: bool       # DiD, ITS
    requires_time_series: bool    # ITS
    requires_cluster_assignment: bool

    # UI metadata
    featured: bool = False

    calculator_header: Optional[dict] = None
    calculator_config: Optional[dict] = None
    calculator_background: Optional[str] = None



DESIGNS: List[DesignInfo] = [

    # ─────────────────────────────────────────────────────────────
    # Individual Random Assignment (IRA)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="IRA",
        title="Simple Individual Random Assignment",
        description="Individuals are randomly assigned without blocking.",
        icon="🧍",
        page="pages/IRA.py",
        is_blocked=False,
        levels=1,
        assignment_unit="individual",
        assignment_level=1,
        block_effect=None,
        design_family="IRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    # ─────────────────────────────────────────────────────────────
    # Blocked Individual Random Assignment (BIRA)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="BIRA2_1c",
        title="Blocked Individual Random Assignment (constant block effect)",
        description="Individuals are randomized within blocks; block effects treated as constant (treatment effect does not vary across blocks).",
        icon="🧍",
        page="pages/BIRA2_1c.py",
        is_blocked=True,
        levels=2,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="constant",
        design_family="BIRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="BIRA2_1f",
        title="Blocked Individual Random Assignment (fixed block effect)",
        description="Individuals are randomized within blocks; block effects treated as fixed with block–treatment interactions.",
        icon="🧍",
        page="pages/BIRA2_1f.py",
        is_blocked=True,
        levels=2,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="fixed",
        design_family="BIRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="BIRA2_1r",
        title="Blocked Individual Random Assignment (random block effect)",
        description="Individuals are randomized within blocks; block effects treated as random.",
        icon="🧍",
        page="pages/BIRA2_1r.py",
        is_blocked=True,
        levels=2,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="random",
        design_family="BIRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="BIRA3_1r",
        title="Blocked Individual Random Assignment (3-level, random effects)",
        description="Three-level blocked IRA with random block and cluster effects.",
        icon="🧍",
        page="pages/BIRA3_1r.py",
        is_blocked=True,
        levels=3,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="random",
        design_family="BIRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="BIRA4_1r",
        title="Blocked Individual Random Assignment (4-level, random effects)",
        description="Four-level blocked IRA with random block, site, and cluster effects.",
        icon="🧍",
        page="pages/BIRA4_1r.py",
        is_blocked=True,
        levels=4,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="random",
        design_family="BIRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),
    # ─────────────────────────────────────────────────────────────
    # Cluster Random Assignment (CRA)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="CRA2_2r",
        title="Simple Cluster Random Assignment (2-level)",
        description="Clusters are randomly assigned; analysis at the cluster level.",
        icon="🏫",
        page="pages/CRA2_2r.py",
        is_blocked=False,
        levels=2,
        assignment_unit="cluster",
        assignment_level=2,
        block_effect="random",
        design_family="CRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="CRA3_3r",
        title="Simple Cluster Random Assignment (3-level)",
        description="Clusters are randomly assigned in a 3-level structure.",
        icon="🏫",
        page="pages/CRA3_3r.py",
        is_blocked=False,
        levels=3,
        assignment_unit="cluster",
        assignment_level=3,
        block_effect="random",
        design_family="CRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="CRA4_4r",
        title="Simple Cluster Random Assignment (4-level)",
        description="Clusters are randomly assigned in a 4-level structure.",
        icon="🏫",
        page="pages/CRA4_4r.py",
        is_blocked=False,
        levels=4,
        assignment_unit="cluster",
        assignment_level=4,
        block_effect="random",
        design_family="CRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    # ─────────────────────────────────────────────────────────────
    # Blocked Cluster Random Assignment (BCRA)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="BCRA3_2f",
        title="Assumptions",
        description="Hover over the (?) for definitions.",
        icon="",
        page="pages/BCRA3_2f.py",
        is_blocked=True,
        levels=3,
        assignment_unit="cluster",
        assignment_level=2,
        block_effect="fixed",
        design_family="BCRA3_2f",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="BCRA3_2r",
        title="Blocked Cluster Random Assignment (3-level, random block effect)",
        description="Clusters are randomized within blocks; block effects random.",
        icon="🏢",
        page="pages/BCRA3_2r.py",
        is_blocked=True,
        levels=3,
        assignment_unit="cluster",
        assignment_level=2,
        block_effect="random",
        design_family="BCRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="BCRA4_2r",
        title="Blocked Cluster Random Assignment (4-level, random block effect, assignment at level 2)",
        description="Clusters are randomized within blocks in a 4-level structure.",
        icon="🏢",
        page="pages/BCRA4_2r.py",
        is_blocked=True,
        levels=4,
        assignment_unit="cluster",
        assignment_level=2,
        block_effect="random",
        design_family="BCRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="BCRA4_3f",
        title="Blocked Cluster Random Assignment (4-level, fixed block effect, assignment at level 3)",
        description="Clusters are randomized within blocks at level 3.",
        icon="🏢",
        page="pages/BCRA4_3f.py",
        is_blocked=True,
        levels=4,
        assignment_unit="cluster",
        assignment_level=3,
        block_effect="fixed",
        design_family="BCRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    DesignInfo(
        code="BCRA4_3r",
        title="Blocked Cluster Random Assignment (4-level, random block effect, assignment at level 3)",
        description="Clusters are randomized within blocks at level 3.",
        icon="🏢",
        page="pages/BCRA4_3r.py",
        is_blocked=True,
        levels=4,
        assignment_unit="cluster",
        assignment_level=3,
        block_effect="random",
        design_family="BCRA",
        is_randomized=True,
        is_quasi_experimental=False,
        requires_cutoff=False,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=True,
    ),

    # ─────────────────────────────────────────────────────────────
    # Regression Discontinuity (RD)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="RD2_1f",
        title="Regression Discontinuity (2-level, individual assignment, fixed block effect)",
        description="Treatment is assigned by a cutoff; 2-level structure with fixed block effects.",
        icon="📈",
        page="pages/RD2_1f.py",
        is_blocked=True,
        levels=2,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="fixed",
        design_family="RD",
        is_randomized=False,
        is_quasi_experimental=True,
        requires_cutoff=True,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="RD2_1r",
        title="Regression Discontinuity (2-level, individual assignment, random block effect)",
        description="Treatment is assigned by a cutoff; 2-level structure with random block effects.",
        icon="📈",
        page="pages/RD2_1r.py",
        is_blocked=True,
        levels=2,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="random",
        design_family="RD",
        is_randomized=False,
        is_quasi_experimental=True,
        requires_cutoff=True,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),
    DesignInfo(
        code="RD3_1f",
        title="Regression Discontinuity (3-level, individual assignment, fixed block effect)",
        description=(
            "A three-level regression discontinuity design where the highest level "
            "(e.g., districts or sites) is included as fixed effects. Level-3 variance "
            "is absorbed by blocking, and treatment is assigned by a cutoff on a "
            "running variable."
        ),
        icon="📉",
        page="pages/RD3_1f.py",
        is_blocked=True,
        levels=3,
        assignment_unit="individual",
        assignment_level=1,
        block_effect="fixed",
        design_family="RD",
        is_randomized=False,
        is_quasi_experimental=True,
        requires_cutoff=True,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

    DesignInfo(
        code="RD3_1r",
        title="Regression Discontinuity (3-level, individual assignment, unblocked)",
        description=(
            "A three-level regression discontinuity design without blocking at the "
            "highest level. Level-3 variance contributes to the MDES, and covariates "
            "at all levels may reduce residual variance. Treatment is assigned by a "
            "cutoff on a running variable."
        ),
        icon="📈",
        page="pages/RD3_1r.py",
        is_blocked=False,
        levels=3,
        assignment_unit="individual",
        assignment_level=1,
        block_effect=None,
        design_family="RD",
        is_randomized=False,
        is_quasi_experimental=True,
        requires_cutoff=True,
        requires_pre_post=False,
        requires_time_series=False,
        requires_cluster_assignment=False,
    ),

  
    # ─────────────────────────────────────────────────────────────
    # Interrupted Time Series (ITS)
    # ─────────────────────────────────────────────────────────────
    DesignInfo(
        code="ITS",
        title="Interrupted Time Series",
        description=(
            "A quasi-experimental design using segmented regression on a single "
            "time series with pre- and post-intervention periods. Autocorrelation "
            "and the number of time points determine statistical power."
        ),
        icon="⏱️",
        page="pages/ITS.py",
        is_blocked=False,
        levels=1,
        assignment_unit=None,
        assignment_level=None,
        block_effect=None,
        design_family="ITS",
        is_randomized=False,
        is_quasi_experimental=True,
        requires_cutoff=False,
        requires_pre_post=True,
        requires_time_series=True,
        requires_cluster_assignment=False,
    ),

]

from config.calculator_defaults import FAMILY_HEADERS, DESIGN_CONFIGS
from config.backgrounds import FAMILY_BACKGROUNDS

ENRICHED_DESIGNS = []
for d in DESIGNS:
    header = FAMILY_HEADERS.get(d.design_family)
    config = DESIGN_CONFIGS.get(d.code)
    background = FAMILY_BACKGROUNDS.get(d.design_family)

    ENRICHED_DESIGNS.append(
        d._replace(
            calculator_header=header,
            calculator_config=config,
            calculator_background=background,
        )
    )

DESIGNS = ENRICHED_DESIGNS

# ─────────────────────────────────────────────────────────────
# Lookup tables
# ─────────────────────────────────────────────────────────────

DESIGN_BY_CODE: Dict[str, DesignInfo] = {d.code: d for d in DESIGNS}
PAGE_BY_CODE: Dict[str, str] = {d.code: d.page for d in DESIGNS}