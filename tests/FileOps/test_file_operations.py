import os
import pathlib
import subprocess
import sys
import shutil


def test_multiple_input_files():
    """
    Test vspace with multiple .in files.

    Verifies that parameters in different files are handled correctly
    and all files are copied to output directories.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "MultiFile_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with earth.in and sun.in
    subprocess.check_output(["vspace", "-f", "vspace_multifile.in"], cwd=path)

    # Grab the output folders
    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Test 1: Should have trials (2 semi x 2 mass = 4 trials)
    assert len(folders) == 4, f"Should have 4 trials (2x2), got {len(folders)}"

    # Test 2: Each folder should contain both earth.in and sun.in
    for folder in folders:
        earth_file = os.path.join(folder, "earth.in")
        sun_file = os.path.join(folder, "sun.in")

        assert os.path.exists(earth_file), \
            f"earth.in should exist in {os.path.basename(folder)}"
        assert os.path.exists(sun_file), \
            f"sun.in should exist in {os.path.basename(folder)}"

    # Test 3: Verify parameters in correct files
    for folder in folders:
        # Read earth.in - should have dSemi modified
        with open(os.path.join(folder, "earth.in"), "r") as f:
            earth_content = f.read()
            assert "dSemi" in earth_content, "earth.in should contain dSemi"

        # Read sun.in - should have dMass modified
        with open(os.path.join(folder, "sun.in"), "r") as f:
            sun_content = f.read()
            assert "dMass" in sun_content, "sun.in should contain dMass"

    print("All multiple input files tests passed!")


def test_option_addition():
    """
    Test adding an option that doesn't exist in template.

    Verifies that new options are appended to the file.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "OptionAdd_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "-f", "vspace_option_add.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])

    # Test: New parameter should be in output file
    for folder in folders:
        with open(os.path.join(folder, "planet.in"), "r") as f:
            content = f.read()

        # dRotPeriod wasn't in template, should be added
        assert "dRotPeriod" in content, \
            "New parameter dRotPeriod should be added to file"

        # Should appear somewhere in the file
        lines = content.split('\n')
        rot_lines = [l for l in lines if l.strip().startswith("dRotPeriod")]
        assert len(rot_lines) >= 1, \
            "dRotPeriod should appear in output"

    print("All option addition tests passed!")


def test_option_replacement():
    """
    Test replacing an existing option in template.

    Verifies that existing options are correctly replaced with new values.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "OptionReplace_Test"

    if dir.exists():
        shutil.rmtree(dir)

    subprocess.check_output(["vspace", "-f", "vspace_option_replace.in"], cwd=path)

    folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
    assert len(folders) == 2, "Should have 2 trials"

    # Test: Replaced values should match grid
    expected_masses = [0.5, 1.5]
    actual_masses = []

    for folder in folders:
        with open(os.path.join(folder, "planet.in"), "r") as f:
            for line in f:
                if line.strip().startswith("dMass"):
                    actual_masses.append(float(line.split()[1]))
                    break

    actual_masses.sort()
    assert len(actual_masses) == 2, "Should have 2 mass values"
    assert all(abs(a - e) < 0.001 for a, e in zip(actual_masses, expected_masses)), \
        f"Mass values should be {expected_masses}, got {actual_masses}"

    print("All option replacement tests passed!")


def test_source_folder_with_tilde():
    """
    Test that ~ expansion works for source folder paths.

    Tests lines 92-94 in vspace.py.
    """
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # Create a test directory in home folder temporarily
    home_test_dir = pathlib.Path.home() / ".vspace_test_temp"
    home_test_dir.mkdir(exist_ok=True)

    # Create a simple template file
    (home_test_dir / "test.in").write_text("dMass 1.0\n")

    try:
        # Create vspace input with ~ path
        vspace_input = path / "vspace_tilde_test.in"
        vspace_input.write_text(f"""srcfolder     ~/.vspace_test_temp
destfolder    Tilde_Test
trialname     tilde
samplemode    grid

file test.in
dMass [0.5, 1.5, n2] mass
""")

        dir = path / "Tilde_Test"
        if dir.exists():
            shutil.rmtree(dir)

        # Run vspace
        subprocess.check_output(["vspace", "-f", "vspace_tilde_test.in"], cwd=path)

        # Verify it worked
        folders = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
        assert len(folders) == 2, "Should have 2 trials from ~-expanded path"

        print("All tilde expansion tests passed!")

    finally:
        # Cleanup
        if home_test_dir.exists():
            shutil.rmtree(home_test_dir)
        if vspace_input.exists():
            vspace_input.unlink()


if __name__ == "__main__":
    test_multiple_input_files()
    test_option_addition()
    test_option_replacement()
    test_source_folder_with_tilde()
