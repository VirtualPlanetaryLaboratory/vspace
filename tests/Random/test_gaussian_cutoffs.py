import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_gaussian_min_cutoff():
    """
    Test Gaussian distribution with minimum cutoff.

    Tests resampling logic (lines 393-403) that rejects values below min_cutoff.
    All samples should be >= min_cutoff value.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Gaussian_MinCutoff_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace: Gaussian(0, 1) with min=-1.0
    subprocess.check_output(["vspace", "-f", "vspace_gaussian_min.in"], cwd=path, stderr=subprocess.STDOUT)

    # Extract values
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test 1: All values >= min cutoff
    assert len(values) == 100, "Should have 100 samples"
    assert np.all(values >= -1.0), \
        f"All values should be >= -1.0, min was {np.min(values):.3f}"

    # Test 2: Distribution should still be approximately Gaussian above cutoff
    # Mean should be shifted above 0 due to truncation
    mean = np.mean(values)
    assert mean > 0.0, \
        f"Mean should be > 0 due to min cutoff, got {mean:.3f}"

    # Test 3: Some values should be close to the cutoff
    # (verifies resampling is working, not just shifting distribution)
    near_cutoff = np.sum((values >= -1.0) & (values < -0.5))
    assert near_cutoff > 0, \
        "Some values should be near the min cutoff boundary"

    print("All Gaussian min cutoff tests passed!")


def test_gaussian_max_cutoff():
    """
    Test Gaussian distribution with maximum cutoff.

    Tests resampling logic (lines 404-414) that rejects values above max_cutoff.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Gaussian_MaxCutoff_Test"

    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace: Gaussian(0, 1) with max=1.0
    subprocess.check_output(["vspace", "-f", "vspace_gaussian_max.in"], cwd=path, stderr=subprocess.STDOUT)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test 1: All values <= max cutoff
    assert len(values) == 100, "Should have 100 samples"
    assert np.all(values <= 1.0), \
        f"All values should be <= 1.0, max was {np.max(values):.3f}"

    # Test 2: Mean should be shifted below 0
    mean = np.mean(values)
    assert mean < 0.0, \
        f"Mean should be < 0 due to max cutoff, got {mean:.3f}"

    # Test 3: Some values should be close to the cutoff
    near_cutoff = np.sum((values > 0.5) & (values <= 1.0))
    assert near_cutoff > 0, \
        "Some values should be near the max cutoff boundary"

    print("All Gaussian max cutoff tests passed!")


def test_gaussian_both_cutoffs():
    """
    Test Gaussian distribution with both min and max cutoffs.

    Tests resampling logic (lines 415-429) for bounded Gaussian.
    All samples should be in [min, max] range.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Gaussian_BothCutoffs_Test"

    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace: Gaussian(0, 1) with min=-1.5, max=1.5
    subprocess.check_output(["vspace", "-f", "vspace_gaussian_both.in"], cwd=path, stderr=subprocess.STDOUT)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    values = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values.append(float(line.split()[1]))

    values = np.array(values)

    # Test 1: All values within [min, max]
    assert len(values) == 100, "Should have 100 samples"
    assert np.all(values >= -1.5), \
        f"All values should be >= -1.5, min was {np.min(values):.3f}"
    assert np.all(values <= 1.5), \
        f"All values should be <= 1.5, max was {np.max(values):.3f}"

    # Test 2: Mean should still be approximately 0
    # With symmetric cutoffs at ±1.5σ, mean shouldn't shift much
    mean = np.mean(values)
    assert -0.3 < mean < 0.3, \
        f"Mean should be ~0 with symmetric cutoffs, got {mean:.3f}"

    # Test 3: Values should span most of the allowed range
    value_range = np.max(values) - np.min(values)
    assert value_range > 2.5, \
        f"Values should span most of [-1.5, 1.5], got range {value_range:.2f}"

    # Test 4: Some values near each boundary
    near_min = np.sum((values >= -1.5) & (values < -1.0))
    near_max = np.sum((values > 1.0) & (values <= 1.5))
    assert near_min > 0, "Some values should be near min cutoff"
    assert near_max > 0, "Some values should be near max cutoff"

    print("All Gaussian both cutoffs tests passed!")


if __name__ == "__main__":
    test_gaussian_min_cutoff()
    test_gaussian_max_cutoff()
    test_gaussian_both_cutoffs()
