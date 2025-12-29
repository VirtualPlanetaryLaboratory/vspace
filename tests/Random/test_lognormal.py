import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_lognormal_basic():
    """
    Test basic log-normal distribution sampling.

    Log-normal distribution: if X ~ LogNormal(μ, σ), then log(X) ~ Normal(μ, σ).
    Tests lines 460-520.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "LogNormal_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed
    # Using mean=0, sigma=1 for standard log-normal
    subprocess.check_output(["vspace", "vspace_lognormal.in"], cwd=path)

    # Grab the output folders
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Extract parameter values
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test 1: Correct number of samples
    assert len(values) == 100, "Should have 100 samples (randsize=100)"

    # Test 2: All values must be positive (property of log-normal)
    assert np.all(values > 0.0), "All log-normal values must be positive"

    # Test 3: log(values) should follow normal distribution
    # For LogNormal(0, 1), log(values) ~ Normal(0, 1)
    log_values = np.log(values)

    # Mean of log(values) should be ~0.0
    # SE = 1/sqrt(100) = 0.1, use 3*SE = 0.3
    log_mean = np.mean(log_values)
    assert -0.3 < log_mean < 0.3, \
        f"Mean of log(values) should be ~0.0, got {log_mean:.3f}"

    # Std of log(values) should be ~1.0
    # SE ≈ 1/sqrt(200) ≈ 0.07, use 3*SE = 0.2
    log_std = np.std(log_values, ddof=1)
    assert 0.8 < log_std < 1.2, \
        f"Std of log(values) should be ~1.0, got {log_std:.3f}"

    # Test 4: Median of log-normal(0,1) should be exp(0) = 1.0
    # (median is more robust than mean for log-normal)
    median_value = np.median(values)
    assert 0.8 < median_value < 1.2, \
        f"Median should be ~1.0, got {median_value:.3f}"

    # Test 5: Values should span multiple orders of magnitude
    # (characteristic of log-normal)
    value_range = np.max(values) / np.min(values)
    assert value_range > 10, \
        f"Log-normal should span multiple orders of magnitude, got range {value_range:.1f}"

    print("All basic log-normal distribution tests passed!")


def test_lognormal_nonstandard():
    """
    Test log-normal distribution with non-standard parameters.

    Using mean=1.0, sigma=0.5 to verify parameter handling.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "LogNormal_Nonstandard_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "vspace_lognormal_nonstandard.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test: log(values) should follow Normal(1.0, 0.5)
    log_values = np.log(values)

    # Mean of log(values) should be ~1.0
    # SE = 0.5/sqrt(100) = 0.05, use 3*SE = 0.15
    log_mean = np.mean(log_values)
    assert 0.85 < log_mean < 1.15, \
        f"Mean of log(values) should be ~1.0, got {log_mean:.3f}"

    # Std of log(values) should be ~0.5
    # SE ≈ 0.5/sqrt(200) ≈ 0.035, use 3*SE ≈ 0.1
    log_std = np.std(log_values, ddof=1)
    assert 0.4 < log_std < 0.6, \
        f"Std of log(values) should be ~0.5, got {log_std:.3f}"

    # Median should be exp(1.0) ≈ 2.718
    median_value = np.median(values)
    assert 2.4 < median_value < 3.0, \
        f"Median should be ~e ≈ 2.718, got {median_value:.3f}"

    print("All non-standard log-normal distribution tests passed!")


if __name__ == "__main__":
    test_lognormal_basic()
    test_lognormal_nonstandard()
