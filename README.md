# 🔬 MDES Calculator

**Modern, browser-based Minimum Detectable Effect Size (MDES) calculator for
multilevel randomized trials.**

Built with [Streamlit](https://streamlit.io/), this tool helps education,
medical, public-health, psychology, and social-science researchers determine
the smallest effect their cluster randomized trial can reliably detect.

---

## ✨ Features

- **Plain-language design tiles** – choose your design from descriptive cards,
  not cryptic codes.
- **Guided questionnaire** – answer a few questions to identify your design.
- **Natural-language classifier** – paste a study description; the tool will
  suggest the right design.
- **Supported designs:**

  | Code | Description |
  |------|-------------|
  | `CRA2_2` | Clusters (e.g., classrooms, schools) randomized – 2-level CRT |
  | `BCRA2_2` | Clusters randomized within blocks – blocked 2-level CRT |
  | `CRA3_3` | Top-level orgs (e.g., districts) randomized – 3-level CRT |
  | `BCRA3_2` | Schools randomized within districts (districts as blocks) |

- **Continuous and binary outcomes** – MDES in standardized units,
  percentage points, and raw units.
- **Design effect & effective sample size** reported alongside MDES.
- **Interactive visualizations** – MDES vs. sample-size curves.
- **One-click download** – plain-text summary of all inputs and results.

---

## 🚀 Running locally

### Prerequisites

- Python 3.10 or later
- `pip`

### Steps

```bash
# Clone the repository
git clone https://github.com/Havala-Hanson/mdescalculator.git
cd mdescalculator

# (Optional) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🗂️ Project structure

```
mdescalculator/
├── app.py                    # Landing page: design tiles + classifier
├── pages/
│   ├── 1_Two_Level_CRT.py    # CRA2_2 calculator
│   ├── 2_Three_Level_CRT.py  # CRA3_3 and BCRA3_2 calculators
│   └── 3_Blocked_Design.py   # BCRA2_2 calculator
├── mdes_engines/
│   ├── __init__.py           # Public API
│   ├── mdes_two_level.py     # CRA2_2 engine
│   ├── mdes_three_level.py   # CRA3_3 and BCRA3_2 engines
│   └── mdes_blocked.py       # BCRA2_2 engine
├── requirements.txt
├── LICENSE                   # MIT
└── README.md
```

---

## 📐 Statistical formulas

### Two-level CRT (CRA2_2)

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho\,(1 - R^2_2)}{P(1-P)\,J}
    +\frac{(1-\rho)\,(1 - R^2_1)}{P(1-P)\,J\,n}
},\quad \nu = J - 2
$$

### Three-level CRT (CRA3_3)

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho_3\,(1-R^2_3)}{P(1-P)\,K}
    +\frac{\rho_2\,(1-R^2_2)}{P(1-P)\,K\,J}
    +\frac{(1-\rho_3-\rho_2)\,(1-R^2_1)}{P(1-P)\,K\,J\,n}
},\quad \nu = K - 2
$$

### Blocked designs

Blocked designs use the same σ_δ formula as their unblocked counterparts, but
degrees of freedom are reduced by the number of blocks:

- BCRA2_2: ν = J − 2B  
- BCRA3_2: ν = K(J − 2)

**References:**
- Bloom, H. S., Richburg-Hayes, L., & Black, A. R. (2007). Using covariates to improve precision for studies that randomize schools. *Educational Evaluation and Policy Analysis*, 29(1), 30–59.
- Dong, N., & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum detectable effect sizes. *Journal of Research on Educational Effectiveness*, 6(1), 24–67.

---

## 🗺️ Roadmap

- [ ] Add support for individual-level (non-clustered) randomized designs
- [ ] Add quasi-experimental designs (regression discontinuity, diff-in-diff)
- [ ] Interactive sensitivity analysis tables (vary ICC across a range)
- [ ] Required sample size calculator (given a target MDES)
- [ ] Export results to PDF or Excel
- [ ] Multilingual interface

---

## 📄 License

MIT © 2026 Havala Hanson, Ph.D.  
See [LICENSE](LICENSE) for details.
