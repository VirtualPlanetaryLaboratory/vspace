import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_sine_degrees():
    """
    Test uniform sampling in sine of angle (degrees).

    For uniform distribution in sin(θ), the angle distribution should be
    denser near 0° and 90° and sparser near 45°.

    Tests lines 571-615 with degree angle units.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Sine_Degrees_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with fixed seed for reproducibility
    subprocess.check_output(["vspace", "vspace_sine_deg.in"], cwd=path)

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

    # Test 3: sin(angles) should be uniform in [sin(0), sin(90)] = [0, 1]
    sin_values = np.sin(np.radians(angles))
    assert np.all(sin_values >= 0.0), "All sin values should be >= 0.0"
    assert np.all(sin_values <= 1.0), "All sin values should be <= 1.0"

    # Test 4: Mean of sin(angles) should be ~0.5 (uniform in [0,1])
    # With 100 samples, SE = sqrt((1/12)/100) ≈ 0.029, use 3*SE ≈ 0.09
    sin_mean = np.mean(sin_values)
    assert 0.4 < sin_mean < 0.6, \
        f"Mean of sin(angles) should be ~0.5, got {sin_mean:.3f}"

    # Test 5: Angles should NOT be uniformly distributed
    # (this distinguishes sine sampling from uniform angle sampling)
    # Uniform angles would have mean ≈ 45°, sine-weighted should differ
    angle_mean = np.mean(angles)
    # For uniform in sin, expected mean angle is actually closer to 60°
    # We just verify it's not close to 45° (which would indicate uniform angles)
    assert not (43 < angle_mean < 47), \
        f"Angle distribution should not be uniform (mean {angle_mean:.1f}° suggests sine weighting)"

    # Test 6: Validate rand_list.dat
    rand_list_file = dir / "rand_list.dat"
    assert rand_list_file.exists(), "rand_list.dat should be created"

    print("All sine distribution (degrees) tests passed!")


def test_sine_radians():
    """
    Test uniform sampling in sine of angle (radians).

    Same statistical properties as degree test, but with radian units.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "Sine_Radians_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "vspace_sine_rad.in"], cwd=path)

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

    # Test 2: sin(angles) uniform in [0, 1]
    sin_values = np.sin(angles)
    assert np.all(sin_values >= 0.0), "All sin values should be >= 0.0"
    assert np.all(sin_values <= 1.0), "All sin values should be <= 1.0"

    # Test 3: Mean of sin values ~0.5
    sin_mean = np.mean(sin_values)
    assert 0.4 < sin_mean < 0.6, \
        f"Mean of sin(angles) should be ~0.5, got {sin_mean:.3f}"

    # Test 4: Angles not uniformly distributed
    angle_mean = np.mean(angles)
    # For uniform angles in [0, π/2], mean would be π/4 ≈ 0.785
    # For sine-weighted, it differs
    assert not (0.75 < angle_mean < 0.82), \
        f"Angle mean ({angle_mean:.3f}) should differ from uniform (π/4 ≈ 0.785)"

    print("All sine distribution (radians) tests passed!")


if __name__ == "__main__":
    test_sine_degrees()
    test_sine_radians()
