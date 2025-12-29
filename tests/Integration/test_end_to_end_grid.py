"""
End-to-end integration tests for grid mode.

This module tests realistic multi-file, multi-parameter grid mode workflows
with comprehensive validation of all outputs.
"""

import pytest
import subprocess
import shutil
from pathlib import Path
import numpy as np


def test_realistic_grid_sweep():
    """
    Test realistic grid sweep with multiple files and parameters.

    Simulates a real research workflow:
    - earth.in: dSemi (3 values), dEcc (2 values)
    - sun.in: dMass (2 values)
    - Total: 3x2x2 = 12 trials
    """
    test_dir = Path(__file__).parent / "RealisticGrid_Test"
    test_dir.mkdir(exist_ok=True)

    # Create template files
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)

    (template_dir / "earth.in").write_text("""# Earth input file
sName         Earth
dMass         -1.0
dRadius       -1.0
dSemi         1.0
dEcc          0.0167
dObliquity    23.5
""")

    (template_dir / "sun.in").write_text("""# Sun input file
sName         Sun
dMass         1.0
dAge          5e9
dLuminosity   1.0
""")

    (template_dir / "vpl.in").write_text("""# VPLanet input file
sSystemName   SolarSystem
bOverwrite    1
""")

    # Create vspace.in
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder RealisticGrid
trialname solar
samplemode grid

file earth.in
dSemi [0.8, 1.2, n3] semi
dEcc [0.0, 0.2, n2] ecc

file sun.in
dMass [0.9, 1.1, n2] mass

file vpl.in
""")

    # Run vspace
    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    # Verify output directory structure
    output_dir = test_dir / "RealisticGrid"
    assert output_dir.exists(), "Output directory not created"

    # Should have 12 trial directories (3x2x2)
    trial_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()])
    assert len(trial_dirs) == 12, f"Expected 12 trials, got {len(trial_dirs)}"

    # Verify grid_list.dat
    grid_list = output_dir / "grid_list.dat"
    assert grid_list.exists(), "grid_list.dat not created"

    with open(grid_list) as f:
        lines = f.readlines()

    # Check header
    header = lines[0].strip()
    assert "earth/dSemi" in header, "Header missing earth/dSemi"
    assert "earth/dEcc" in header, "Header missing earth/dEcc"
    assert "sun/dMass" in header, "Header missing sun/dMass"

    # Check data lines (skip header)
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 12, f"Expected 12 data lines, got {len(data_lines)}"

    # Verify all parameter combinations present
    expected_semi = [0.8, 1.0, 1.2]
    expected_ecc = [0.0, 0.2]
    expected_mass = [0.9, 1.1]

    combinations_found = set()
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 4:
            semi = float(parts[1])
            ecc = float(parts[2])
            mass = float(parts[3])
            combinations_found.add((semi, ecc, mass))

    # Generate all expected combinations
    expected_combinations = set()
    for semi in expected_semi:
        for ecc in expected_ecc:
            for mass in expected_mass:
                expected_combinations.add((semi, ecc, mass))

    assert combinations_found == expected_combinations, \
        f"Combinations mismatch.\nExpected: {expected_combinations}\nGot: {combinations_found}"

    # Verify file contents in a sample trial
    sample_trial = trial_dirs[0]

    # Check earth.in
    earth_file = sample_trial / "earth.in"
    assert earth_file.exists(), f"earth.in not found in {sample_trial.name}"
    earth_contents = earth_file.read_text()
    assert "dSemi" in earth_contents, "dSemi not in earth.in"
    assert "dEcc" in earth_contents, "dEcc not in earth.in"
    assert "dObliquity" in earth_contents, "Original parameter dObliquity missing"

    # Check sun.in
    sun_file = sample_trial / "sun.in"
    assert sun_file.exists(), f"sun.in not found in {sample_trial.name}"
    sun_contents = sun_file.read_text()
    assert "dMass" in sun_contents, "dMass not in sun.in"
    assert "dAge" in sun_contents, "Original parameter dAge missing"

    # Check vpl.in was copied
    vpl_file = sample_trial / "vpl.in"
    assert vpl_file.exists(), f"vpl.in not found in {sample_trial.name}"

    # Verify directory naming convention
    # Should be like: solarsemi0_ecc0_mass0, solarsemi0_ecc0_mass1, etc.
    for trial_dir in trial_dirs:
        name = trial_dir.name
        assert name.startswith("solar"), f"Trial name doesn't start with 'solar': {name}"
        assert "semi" in name, f"Trial name missing semi index: {name}"
        assert "ecc" in name, f"Trial name missing ecc index: {name}"
        assert "mass" in name, f"Trial name missing mass index: {name}"

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
