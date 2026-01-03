import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_uniform_distribution():
    """
    Test uniform random distribution sampling.

    Validates:
    - All samples are within [low, high] range
    - Mean is approximately (low + high) / 2
    - Standard deviation is approximately (high - low) / sqrt(12)
    - rand_list.dat is created with correct format
    - Histogram PDF is generated
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Uniform_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "-f", "vspace.in"], cwd=path)

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

    # Test 2: All values within range [1.0, 2.0]
    assert np.all(values >= 1.0), "All values should be >= 1.0"
    assert np.all(values <= 2.0), "All values should be <= 2.0"

    # Test 3: Mean should be approximately 1.5 (midpoint)
    # For uniform [1, 2], expected mean = 1.5
    # With 100 samples, allow ±0.1 tolerance
    assert 1.4 < np.mean(values) < 1.6, \
        f"Mean should be ~1.5, got {np.mean(values):.3f}"

    # Test 4: Standard deviation check
    # For uniform [a, b], std = (b - a) / sqrt(12) ≈ 0.289
    # With 100 samples, allow ±0.1 tolerance
    expected_std = (2.0 - 1.0) / np.sqrt(12)  # ≈ 0.289
    assert 0.2 < np.std(values) < 0.4, \
        f"Std should be ~{expected_std:.3f}, got {np.std(values):.3f}"

    # Test 5: Validate rand_list.dat format
    rand_list_file = dir / "rand_list.dat"
    assert rand_list_file.exists(), "rand_list.dat should be created"

    with open(rand_list_file, "r") as f:
        lines = f.readlines()
        # Check header
        assert lines[0].strip().startswith("trial"), \
            "First line should be header starting with 'trial'"
        assert "earth/dSemi" in lines[0], \
            "Header should contain 'earth/dSemi'"
        # Check number of data lines (header + 100 samples)
        assert len(lines) == 101, \
            f"Should have 101 lines (1 header + 100 data), got {len(lines)}"

    # Test 6: Validate histogram was generated
    hist_file = dir / "hist_earth_dSemi.pdf"
    assert hist_file.exists(), \
        "Histogram PDF should be generated in destination directory"

    print("All uniform distribution tests passed!")


if __name__ == "__main__":
    test_uniform_distribution()
