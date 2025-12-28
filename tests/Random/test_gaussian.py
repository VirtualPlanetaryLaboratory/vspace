import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_gaussian_basic():
    """
    Test basic Gaussian distribution sampling.

    Validates:
    - Standard normal distribution (mean=0, sigma=1)
    - Statistical properties match expected distribution
    - No crashes or errors
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Gaussian_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "vspace_gaussian.in"], cwd=path)

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

    # Test 2: Mean should be approximately 0.0 (specified mean)
    # With 100 samples from N(0,1), standard error = 1/sqrt(100) = 0.1
    # Use 3*SE = 0.3 as tolerance
    mean = np.mean(values)
    assert -0.3 < mean < 0.3, \
        f"Mean should be ~0.0, got {mean:.3f}"

    # Test 3: Standard deviation should be approximately 1.0
    # For n=100, SE of std is approximately 1/sqrt(2*100) ≈ 0.07
    # Use 3*SE = 0.2 as tolerance
    std = np.std(values, ddof=1)  # Use sample std
    assert 0.8 < std < 1.2, \
        f"Std should be ~1.0, got {std:.3f}"

    # Test 4: Most values should be within ±3 sigma
    # For normal distribution, 99.7% should be within ±3σ
    in_range = np.sum(np.abs(values) <= 3.0)
    assert in_range >= 95, \
        f"At least 95/100 values should be within ±3σ, got {in_range}/100"

    # Test 5: Validate rand_list.dat format
    rand_list_file = dir / "rand_list.dat"
    assert rand_list_file.exists(), "rand_list.dat should be created"

    with open(rand_list_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 101, \
            f"Should have 101 lines (1 header + 100 data), got {len(lines)}"

    print("All basic Gaussian distribution tests passed!")


def test_gaussian_nonstandard():
    """
    Test Gaussian distribution with non-standard parameters.

    Tests mean=10.0, sigma=2.0 to verify parameter handling.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Gaussian_Nonstandard_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace
    subprocess.check_output(["vspace", "vspace_gaussian_nonstandard.in"], cwd=path)

    # Extract values
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test mean ≈ 10.0
    # SE = 2.0/sqrt(100) = 0.2, use 3*SE = 0.6
    mean = np.mean(values)
    assert 9.4 < mean < 10.6, \
        f"Mean should be ~10.0, got {mean:.3f}"

    # Test std ≈ 2.0
    # SE ≈ 2.0/sqrt(200) ≈ 0.14, use 3*SE = 0.4
    std = np.std(values, ddof=1)
    assert 1.6 < std < 2.4, \
        f"Std should be ~2.0, got {std:.3f}"

    # Most values should be in [10-3*2, 10+3*2] = [4, 16]
    in_range = np.sum((values >= 4.0) & (values <= 16.0))
    assert in_range >= 95, \
        f"At least 95/100 values should be within ±3σ of mean, got {in_range}/100"

    print("All non-standard Gaussian distribution tests passed!")


if __name__ == "__main__":
    test_gaussian_basic()
    test_gaussian_nonstandard()
