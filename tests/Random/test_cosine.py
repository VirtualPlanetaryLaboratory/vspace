import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_cosine_degrees():
    """
    Test uniform sampling in cosine of angle (degrees).

    For uniform distribution in cos(θ), the angle distribution should be
    denser near 0° and 90° and sparser near 45°.

    Tests lines 617-661 with degree angle units.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Cosine_Degrees_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "-f", "vspace_cosine_deg.in"], cwd=path)

    # Grab the output folders
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Extract parameter values (angles in degrees)
    angles = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dInc"):
                    angles.append(float(line.split()[1]))

    angles = np.array(angles)

    # Test 1: Correct number of samples
    assert len(angles) == 100, "Should have 100 samples (randsize=100)"

    # Test 2: All angles within range [0, 90] degrees
    assert np.all(angles >= 0.0), "All angles should be >= 0.0 degrees"
    assert np.all(angles <= 90.0), "All angles should be <= 90.0 degrees"

    # Test 3: cos(angles) should be uniform in [cos(90), cos(0)] = [0, 1]
    # Note: cos is decreasing, so cos(0°)=1, cos(90°)=0
    cos_values = np.cos(np.radians(angles))
    assert np.all(cos_values >= 0.0), "All cos values should be >= 0.0"
    assert np.all(cos_values <= 1.0), "All cos values should be <= 1.0"

    # Test 4: Mean of cos(angles) should be ~0.5 (uniform in [0,1])
    # With 100 samples, SE = sqrt((1/12)/100) ≈ 0.029, use 3*SE ≈ 0.09
    cos_mean = np.mean(cos_values)
    assert 0.4 < cos_mean < 0.6, \
        f"Mean of cos(angles) should be ~0.5, got {cos_mean:.3f}"

    # Test 5: Angles should NOT be uniformly distributed
    # Uniform angles would have mean ≈ 45°, cosine-weighted should differ
    angle_mean = np.mean(angles)
    assert not (43 < angle_mean < 47), \
        f"Angle distribution should not be uniform (mean {angle_mean:.1f}° suggests cosine weighting)"

    # Test 6: Validate rand_list.dat
    rand_list_file = dir / "rand_list.dat"
    assert rand_list_file.exists(), "rand_list.dat should be created"

    print("All cosine distribution (degrees) tests passed!")


def test_cosine_radians():
    """
    Test uniform sampling in cosine of angle (radians).

    Same statistical properties as degree test, but with radian units.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Cosine_Radians_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "-f", "vspace_cosine_rad.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    angles = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            for line in f:
                if line.startswith("dInc"):
                    angles.append(float(line.split()[1]))

    angles = np.array(angles)

    # Test 1: All angles in range [0, π/2] radians
    assert len(angles) == 100, "Should have 100 samples"
    assert np.all(angles >= 0.0), "All angles should be >= 0.0 radians"
    assert np.all(angles <= np.pi/2), "All angles should be <= π/2 radians"

    # Test 2: cos(angles) uniform in [0, 1]
    cos_values = np.cos(angles)
    assert np.all(cos_values >= 0.0), "All cos values should be >= 0.0"
    assert np.all(cos_values <= 1.0), "All cos values should be <= 1.0"

    # Test 3: Mean of cos values ~0.5
    cos_mean = np.mean(cos_values)
    assert 0.4 < cos_mean < 0.6, \
        f"Mean of cos(angles) should be ~0.5, got {cos_mean:.3f}"

    # Test 4: Angles not uniformly distributed
    angle_mean = np.mean(angles)
    # For uniform angles in [0, π/2], mean would be π/4 ≈ 0.785
    assert not (0.75 < angle_mean < 0.82), \
        f"Angle mean ({angle_mean:.3f}) should differ from uniform (π/4 ≈ 0.785)"

    print("All cosine distribution (radians) tests passed!")


if __name__ == "__main__":
    test_cosine_degrees()
    test_cosine_radians()
