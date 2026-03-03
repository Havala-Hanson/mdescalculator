import subprocess
import sys
import importlib.util

# --- Python IRA calculation ---
def python_ira_mdes(n, p=0.5, r21=0, g1=0, alpha=0.05, power=0.80):
    # Dynamically import the compute_mdes_ira function from mdes_engines/ira.py
    spec = importlib.util.spec_from_file_location(
        "ira", "mdes_engines/ira.py"
    )
    ira = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ira)
    # You may need to adjust the function name and arguments to match your code
    result = ira.compute_mdes_ira(
        n_individuals=n,
        r2_level1=r21,
        alpha=alpha,
        power=power,
        outcome_type="continuous"
    )
    return result.mdes

# --- R IRA calculation ---
def r_ira_mdes(n, p=0.5, r21=0, g1=0, alpha=0.05, power=0.80):
    r_script = f"""
    source('docs/ira.r')
    result <- mdes.ira1r1(n={n}, p={p}, r21={r21}, g1={g1}, alpha={alpha}, power={power})
    cat(result$mdes)
    """
    completed = subprocess.run(
        ["Rscript", "-e", r_script],
        capture_output=True,
        text=True
    )
    if completed.returncode != 0:
        print("R error:", completed.stderr)
        sys.exit(1)
    return float(completed.stdout.strip())

# --- Test and compare ---
def test_ira_equivalence():
    n = 200
    p = 0.5
    r21 = 0.1
    g1 = 0
    alpha = 0.05
    power = 0.80

    mdes_py = python_ira_mdes(n, p, r21, g1, alpha, power)
    mdes_r = r_ira_mdes(n, p, r21, g1, alpha, power)

    print(f"Python MDES: {mdes_py}")
    print(f"R MDES: {mdes_r}")
    print(f"Difference: {abs(mdes_py - mdes_r)}")

    assert abs(mdes_py - mdes_r) < 1e-6, "MDES results differ!"

if __name__ == "__main__":
    test_ira_equivalence()