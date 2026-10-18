#!/usr/bin/env python3
"""run_all.py — End-to-end reproduction of the Card & Krueger (1994) replication
project. Run from the repository root:

    python3 code/run_all.py

Generates every table and figure in outputs/ from data/input/public.csv.
No manual editing of data or code is required between steps.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "01_clean_data.py",
    "02_table2.py",
    "03_table3.py",
    "04_table4.py",
    "05_figure1.py",
    "06_extension.py",
    "07_spec_tests.py",
]

def main():
    for s in SCRIPTS:
        print(f"\n{'=' * 70}\n>>> Running {s}\n{'=' * 70}")
        r = subprocess.run([sys.executable, str(ROOT / "code" / s)], cwd=ROOT)
        if r.returncode != 0:
            print(f"FAILED: {s}")
            sys.exit(r.returncode)
    print("\nAll scripts completed successfully.")
    print("Tables:   outputs/tables/")
    print("Figures:  outputs/figures/")

if __name__ == "__main__":
    main()
