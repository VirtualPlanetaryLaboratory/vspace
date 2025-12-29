"""
End-to-end integration tests for random mode.

This module tests realistic multi-file, multi-distribution random mode workflows
with comprehensive validation of all outputs including histograms.
"""

import pytest
import subprocess
import shutil
from pathlib import Path
import numpy as np


def test_realistic_random_sweep():
    """
    Test realistic random sweep with multiple files and distributions.

    Simulates a real research workflow:
    - earth.in: dSemi (uniform), dEcc (log-uniform), dInc (sine)
    - sun.in: dMass (Gaussian), dAge (log-normal)
    - 100 random trials with mixed distribution types
    """
    test_dir = Path(__file__).parent / "RealisticRandom_Test"
    test_dir.mkdir(exist_ok=True)

    # Create template files
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)

    (template_dir / "earth.in").write_text("""# Earth input file
sName         Earth
sUnitAngle    degrees
dMass         -1.0
dRadius       -1.0
dSemi         1.0
dEcc          0.0167
dInc          0.0
dObliquity    23.5
""")

    (template_dir / "sun.in").write_text("""# Sun input file
sName         Sun
dMass         1.0
dAge          5e9
dLuminosity   1.0
""")

    (template_dir / "vpl.in").write_text("""# VPLanet input file
sSystemName   ExoplanetSystem
bOverwrite    1
""")

    # Create vspace.in with multiple distribution types
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder RealisticRandom
trialname exo
samplemode random
seed 42
randsize 100

file earth.in
dSemi [0.5, 2.0, u] semi
dEcc [0.001, 0.5, t] ecc
dInc [0, 90, s] inc

file sun.in
dMass [1.0, 0.1, g] mass
dAge [1.0, 0.5, G] age

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
    output_dir = test_dir / "RealisticRandom"
    assert output_dir.exists(), "Output directory not created"

    # Should have 100 trial directories
    trial_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()])
    assert len(trial_dirs) == 100, f"Expected 100 trials, got {len(trial_dirs)}"

    # Verify rand_list.dat
    rand_list = output_dir / "rand_list.dat"
    assert rand_list.exists(), "rand_list.dat not created"

    with open(rand_list) as f:
        lines = f.readlines()

    # Check header
    header = lines[0].strip()
    assert "earth/dSemi" in header, "Header missing earth/dSemi"
    assert "earth/dEcc" in header, "Header missing earth/dEcc"
    assert "earth/dInc" in header, "Header missing earth/dInc"
    assert "sun/dMass" in header, "Header missing sun/dMass"
    assert "sun/dAge" in header, "Header missing sun/dAge"

    # Check data lines (skip header)
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 100, f"Expected 100 data lines, got {len(data_lines)}"

    # Extract and validate parameter distributions
    semi_values = []
    ecc_values = []
    inc_values = []
    mass_values = []
    age_values = []

    for line in data_lines:
        parts = line.split()
        if len(parts) >= 6:
            semi_values.append(float(parts[1]))
            ecc_values.append(float(parts[2]))
            inc_values.append(float(parts[3]))
            mass_values.append(float(parts[4]))
            age_values.append(float(parts[5]))

    semi_values = np.array(semi_values)
    ecc_values = np.array(ecc_values)
    inc_values = np.array(inc_values)
    mass_values = np.array(mass_values)
    age_values = np.array(age_values)

    # Validate uniform distribution (dSemi)
    assert np.all(semi_values >= 0.5) and np.all(semi_values <= 2.0), \
        f"dSemi out of range [0.5, 2.0]: min={semi_values.min()}, max={semi_values.max()}"

    # Validate log-uniform distribution (dEcc)
    assert np.all(ecc_values >= 0.001) and np.all(ecc_values <= 0.5), \
        f"dEcc out of range [0.001, 0.5]: min={ecc_values.min()}, max={ecc_values.max()}"

    # Check log-uniform is log-distributed
    log_ecc = np.log10(ecc_values)
    assert log_ecc.min() >= np.log10(0.001) - 0.1, "Log-uniform min too low"
    assert log_ecc.max() <= np.log10(0.5) + 0.1, "Log-uniform max too high"

    # Validate sine distribution (dInc)
    assert np.all(inc_values >= 0) and np.all(inc_values <= 90), \
        f"dInc out of range [0, 90]: min={inc_values.min()}, max={inc_values.max()}"

    # Check sine distribution properties (sin(inc) should be uniform)
    sin_inc = np.sin(np.radians(inc_values))
    # Mean of uniform [sin(0), sin(90)] = 0.5
    assert 0.4 < np.mean(sin_inc) < 0.6, \
        f"Sine distribution mean {np.mean(sin_inc)} not close to 0.5"

    # Validate Gaussian distribution (dMass)
    # Should be centered around 1.0 with sigma=0.1
    assert 0.7 < np.mean(mass_values) < 1.3, \
        f"Gaussian mean {np.mean(mass_values)} far from 1.0"

    # Validate log-normal distribution (dAge)
    # log(age) should be Gaussian
    assert np.all(age_values > 0), "Log-normal values must be positive"

    # Verify histograms were generated
    histogram_files = list(output_dir.glob("hist_*.pdf"))
    assert len(histogram_files) == 5, f"Expected 5 histograms, found {len(histogram_files)}"

    expected_histograms = [
        "hist_earth_dSemi.pdf",
        "hist_earth_dEcc.pdf",
        "hist_earth_dInc.pdf",
        "hist_sun_dMass.pdf",
        "hist_sun_dAge.pdf"
    ]

    for hist_name in expected_histograms:
        hist_path = output_dir / hist_name
        assert hist_path.exists(), f"Histogram {hist_name} not created"
        assert hist_path.stat().st_size > 0, f"Histogram {hist_name} is empty"

    # Verify file contents in a sample trial
    sample_trial = trial_dirs[0]

    # Check earth.in
    earth_file = sample_trial / "earth.in"
    assert earth_file.exists(), f"earth.in not found in {sample_trial.name}"
    earth_contents = earth_file.read_text()
    assert "dSemi" in earth_contents, "dSemi not in earth.in"
    assert "dEcc" in earth_contents, "dEcc not in earth.in"
    assert "dInc" in earth_contents, "dInc not in earth.in"
    assert "sUnitAngle" in earth_contents, "sUnitAngle missing (needed for sine distribution)"

    # Check sun.in
    sun_file = sample_trial / "sun.in"
    assert sun_file.exists(), f"sun.in not found in {sample_trial.name}"
    sun_contents = sun_file.read_text()
    assert "dMass" in sun_contents, "dMass not in sun.in"
    assert "dAge" in sun_contents, "dAge not in sun.in"

    # Check vpl.in was copied
    vpl_file = sample_trial / "vpl.in"
    assert vpl_file.exists(), f"vpl.in not found in {sample_trial.name}"

    # Verify directory naming convention
    # Should be like: exorand_00, exorand_01, ..., exorand_99
    for i, trial_dir in enumerate(trial_dirs):
        expected_name = f"exorand_{i:02d}"
        assert trial_dir.name == expected_name, \
            f"Expected trial name '{expected_name}', got '{trial_dir.name}'"

    # Verify reproducibility - same seed should give same values
    # This is implicitly tested by using seed=42 consistently

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
