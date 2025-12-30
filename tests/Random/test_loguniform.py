import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_loguniform_positive():
    """
    Test log-uniform distribution sampling with positive values.

    Validates:
    - All samples are within [low, high] range
    - Log-uniform statistical properties
    - Mean in log-space is approximately (log(low) + log(high)) / 2
    - rand_list.dat is created with correct format
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "LogUniform_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "-f", "vspace_loguniform.in"], cwd=path)

    # Grab the output folders
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Extract parameter values from generated .in files
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    # Convert to numpy array for statistical tests
    values = np.array(values)

    # Test 1: Correct number of samples
    assert len(values) == 100, "Should have 100 samples (randsize=100)"

    # Test 2: All values within range [1.0, 100.0]
    assert np.all(values >= 1.0), "All values should be >= 1.0"
    assert np.all(values <= 100.0), "All values should be <= 100.0"

    # Test 3: Log-uniform means values are uniform in log-space
    # For log-uniform [1, 100], log10(values) should be uniform in [0, 2]
    log_values = np.log10(values)
    assert np.all(log_values >= 0.0), "All log values should be >= 0.0"
    assert np.all(log_values <= 2.0), "All log values should be <= 2.0"

    # Test 4: Mean in log-space should be ~1.0 (midpoint of [0, 2])
    # With 100 samples, allow ±0.2 tolerance
    log_mean = np.mean(log_values)
    assert 0.8 < log_mean < 1.2, \
        f"Log-space mean should be ~1.0, got {log_mean:.3f}"

    # Test 5: Geometric mean should be approximately sqrt(1 * 100) = 10
    # With 100 samples, allow factor of 2 tolerance
    geom_mean = np.exp(np.mean(np.log(values)))
    assert 5.0 < geom_mean < 20.0, \
        f"Geometric mean should be ~10, got {geom_mean:.3f}"

    # Test 6: Validate rand_list.dat format
    rand_list_file = dir / "rand_list.dat"
    assert rand_list_file.exists(), "rand_list.dat should be created"

    with open(rand_list_file, "r") as f:
        lines = f.readlines()
        assert lines[0].strip().startswith("trial"), \
            "First line should be header starting with 'trial'"
        assert "earth/dSemi" in lines[0], \
            "Header should contain 'earth/dSemi'"
        assert len(lines) == 101, \
            f"Should have 101 lines (1 header + 100 data), got {len(lines)}"

    print("All log-uniform distribution tests passed!")


def test_loguniform_negative():
    """
    Test log-uniform distribution with negative values.

    Tests the code path for negative log-uniform sampling (lines 544-554).
    Values should be uniform in log-space in the negative domain.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "LogUniform_Negative_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "-f", "vspace_loguniform_neg.in"], cwd=path)

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

    # Test 1: All values in range [-100.0, -1.0]
    assert len(values) == 100, "Should have 100 samples"
    assert np.all(values >= -100.0), "All values should be >= -100.0"
    assert np.all(values <= -1.0), "All values should be <= -1.0"

    # Test 2: Log of absolute values should be uniform in [0, 2]
    abs_values = np.abs(values)
    log_abs_values = np.log10(abs_values)
    assert np.all(log_abs_values >= 0.0), "All log values should be >= 0.0"
    assert np.all(log_abs_values <= 2.0), "All log values should be <= 2.0"

    # Test 3: Mean in log-space should be ~1.0
    log_mean = np.mean(log_abs_values)
    assert 0.8 < log_mean < 1.2, \
        f"Log-space mean should be ~1.0, got {log_mean:.3f}"

    print("All negative log-uniform distribution tests passed!")


if __name__ == "__main__":
    test_loguniform_positive()
    test_loguniform_negative()
