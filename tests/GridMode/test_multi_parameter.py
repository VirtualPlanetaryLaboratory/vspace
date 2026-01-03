import os
import pathlib
import subprocess
import sys
import shutil
import numpy as np


def test_two_parameters_cartesian_product():
    """
    Test grid mode with 2 parameters to verify cartesian product.

    With dSemi [1, 2, n3] and dEcc [0, 0.2, n3], expect 3x3 = 9 trials.
    Tests the core grid mode logic (lines 838-999).
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "TwoParam_Grid_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace
    subprocess.check_output(["vspace", "-f", "vspace_two_param.in"], cwd=path)

    # Grab the output folders
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Test 1: Correct number of trials (3 x 3 = 9)
    assert len(folders) == 9, f"Should have 9 trials (3x3), got {len(folders)}"

    # Test 2: Extract all parameter combinations
    combinations = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            semi = None
            ecc = None
            for line in f:
                if line.startswith("dSemi"):
                    semi = float(line.split()[1])
                elif line.startswith("dEcc"):
                    ecc = float(line.split()[1])
            if semi is not None and ecc is not None:
                combinations.append((semi, ecc))

    # Test 3: All 9 combinations present
    expected_semi = [1.0, 1.5, 2.0]
    expected_ecc = [0.0, 0.1, 0.2]
    expected_combinations = [(s, e) for s in expected_semi for e in expected_ecc]

    assert len(combinations) == 9, f"Should have 9 combinations, got {len(combinations)}"

    for combo in expected_combinations:
        # Check if this combination exists (with floating point tolerance)
        found = any(np.isclose(c[0], combo[0]) and np.isclose(c[1], combo[1])
                   for c in combinations)
        assert found, f"Missing combination: dSemi={combo[0]}, dEcc={combo[1]}"

    # Test 4: Validate grid_list.dat
    grid_list_file = dir / "grid_list.dat"
    assert grid_list_file.exists(), "grid_list.dat should be created"

    with open(grid_list_file, "r") as f:
        lines = f.readlines()
        # Header + 9 data lines
        assert len(lines) == 10, f"Should have 10 lines (header + 9 data), got {len(lines)}"
        # Check header
        assert "earth/dSemi" in lines[0], "Header should contain earth/dSemi"
        assert "earth/dEcc" in lines[0], "Header should contain earth/dEcc"

    # Test 5: Directory naming should include both parameter indices
    # Example: grid_semi0_ecc0, grid_semi0_ecc1, etc.
    dir_names = [os.path.basename(f) for f in folders]

    # All directories should have both semi and ecc indices
    for name in dir_names:
        assert "semi" in name, f"Directory name should contain 'semi': {name}"
        assert "ecc" in name, f"Directory name should contain 'ecc': {name}"

    print("All two-parameter cartesian product tests passed!")


def test_three_parameters_cube():
    """
    Test grid mode with 3 parameters.

    With 3 parameters each having 2 values, expect 2x2x2 = 8 trials.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "ThreeParam_Grid_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "-f", "vspace_three_param.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Test 1: Should have 2^3 = 8 trials
    assert len(folders) == 8, f"Should have 8 trials (2x2x2), got {len(folders)}"

    # Test 2: Extract all combinations
    combinations = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            semi = None
            ecc = None
            inc = None
            for line in f:
                if line.startswith("dSemi"):
                    semi = float(line.split()[1])
                elif line.startswith("dEcc"):
                    ecc = float(line.split()[1])
                elif line.startswith("dInc"):
                    inc = float(line.split()[1])
            if semi is not None and ecc is not None and inc is not None:
                combinations.append((semi, ecc, inc))

    # Test 3: All 8 combinations present
    expected = [
        (s, e, i)
        for s in [1.0, 2.0]
        for e in [0.0, 0.1]
        for i in [0.0, 45.0]
    ]

    assert len(combinations) == 8, f"Should have 8 combinations"

    for combo in expected:
        found = any(
            np.isclose(c[0], combo[0]) and
            np.isclose(c[1], combo[1]) and
            np.isclose(c[2], combo[2])
            for c in combinations
        )
        assert found, f"Missing combination: {combo}"

    # Test 4: Directory names should have all three indices
    dir_names = [os.path.basename(f) for f in folders]
    for name in dir_names:
        assert "semi" in name and "ecc" in name and "inc" in name, \
            f"Directory should have all three parameter indices: {name}"

    print("All three-parameter cube tests passed!")


def test_mixed_spacing_types():
    """
    Test grid mode with different spacing types in same run.

    Combines linear (n-point), log (l-point), and explicit spacing.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "MixedSpacing_Grid_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "-f", "vspace_mixed_spacing.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # With 3 linear, 2 log, 3 explicit = 3x2x3 = 18 trials
    assert len(folders) == 18, f"Should have 18 trials (3x2x3), got {len(folders)}"

    # Extract combinations and verify spacing types worked correctly
    combinations = []
    for folder in folders:
        with open(os.path.join(folder, "earth.in"), "r") as f:
            semi = None
            mass = None
            radius = None
            for line in f:
                if line.startswith("dSemi"):
                    semi = float(line.split()[1])
                elif line.startswith("dMass"):
                    mass = float(line.split()[1])
                elif line.startswith("dRadius"):
                    radius = float(line.split()[1])
            if semi is not None and mass is not None and radius is not None:
                combinations.append((semi, mass, radius))

    # Verify linear spacing: [1, 2, n3] = [1.0, 1.5, 2.0]
    semis = sorted(set(c[0] for c in combinations))
    assert len(semis) == 3, "Should have 3 unique semi values"
    assert np.allclose(semis, [1.0, 1.5, 2.0]), f"Linear spacing incorrect: {semis}"

    # Verify log spacing: [1, 10, l2] = [1.0, 10.0]
    masses = sorted(set(c[1] for c in combinations))
    assert len(masses) == 2, "Should have 2 unique mass values"
    assert np.allclose(masses, [1.0, 10.0]), f"Log spacing incorrect: {masses}"

    # Verify explicit spacing: [1, 3, 1] = [1.0, 2.0, 3.0]
    radii = sorted(set(c[2] for c in combinations))
    assert len(radii) == 3, "Should have 3 unique radius values"
    assert np.allclose(radii, [1.0, 2.0, 3.0]), f"Explicit spacing incorrect: {radii}"

    print("All mixed spacing type tests passed!")


if __name__ == "__main__":
    test_two_parameters_cartesian_product()
    test_three_parameters_cube()
    test_mixed_spacing_types()
