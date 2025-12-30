import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_seed_reproduces_identical_values():
    """
    Test that same seed produces bit-identical random samples.

    This is critical for scientific reproducibility - researchers must be able
    to regenerate exact parameter sweeps for validation and publication.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # First run with seed=12345
    dir1 = path / "Seed_Test_Run1"
    if dir1.exists():
        shutil.rmtree(dir1)

    subprocess.check_output(["vspace", "-f", "vspace_seed_test.in"], cwd=path)

    # Extract values from first run
    folders1 = sorted([f.path for f in os.scandir(dir1) if f.is_dir()])
    values1 = []
    for folder in folders1:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values1.append(float(line.split()[1]))

    values1 = np.array(values1)

    # Clean up first run
    shutil.rmtree(dir1)

    # Second run with same seed=12345
    subprocess.check_output(["vspace", "-f", "vspace_seed_test.in"], cwd=path)

    # Extract values from second run
    folders2 = sorted([f.path for f in os.scandir(dir1) if f.is_dir()])
    values2 = []
    for folder in folders2:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values2.append(float(line.split()[1]))

    values2 = np.array(values2)

    # Test 1: Same number of values
    assert len(values1) == len(values2), \
        f"Both runs should have same length, got {len(values1)} and {len(values2)}"

    # Test 2: Bit-identical values
    assert np.array_equal(values1, values2), \
        "Same seed should produce bit-identical values"

    # Test 3: Verify exact match (use allclose for floating point comparison)
    assert np.allclose(values1, values2, rtol=0, atol=0), \
        "Values should be exactly identical, not just close"

    # Test 4: Verify values are actually random (not all the same)
    assert len(np.unique(values1)) > 50, \
        "Values should be diverse, not constant"

    print(f"Seed reproducibility test passed! {len(values1)} values matched exactly.")


def test_different_seeds_produce_different_values():
    """
    Test that different seeds produce different random sequences.

    This ensures the RNG is actually being seeded properly.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # Run with seed=12345
    dir1 = path / "Seed_Test_Run1"
    if dir1.exists():
        shutil.rmtree(dir1)

    subprocess.check_output(["vspace", "-f", "vspace_seed_test.in"], cwd=path)

    folders1 = sorted([f.path for f in os.scandir(dir1) if f.is_dir()])
    values1 = []
    for folder in folders1:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values1.append(float(line.split()[1]))

    values1 = np.array(values1)
    shutil.rmtree(dir1)

    # Run with seed=54321
    dir2 = path / "Seed_Test_Run2"
    if dir2.exists():
        shutil.rmtree(dir2)

    subprocess.check_output(["vspace", "-f", "vspace_seed_test2.in"], cwd=path)

    folders2 = sorted([f.path for f in os.scandir(dir2) if f.is_dir()])
    values2 = []
    for folder in folders2:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dSemi"):
                    values2.append(float(line.split()[1]))

    values2 = np.array(values2)

    # Test: Values should be different
    assert not np.array_equal(values1, values2), \
        "Different seeds should produce different values"

    # Test: At least 80% of values should be different
    # (extremely unlikely for 100 random samples to match by chance)
    different_count = np.sum(values1 != values2)
    assert different_count >= 80, \
        f"At least 80/100 values should differ, got {different_count}/100"

    print(f"Different seeds test passed! {different_count}/100 values differed.")


if __name__ == "__main__":
    test_seed_reproduces_identical_values()
    test_different_seeds_produce_different_values()
