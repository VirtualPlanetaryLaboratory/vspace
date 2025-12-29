"""
Tests for vspace validation errors and error handling.

This module tests that vspace properly validates input and raises appropriate
errors for invalid configurations.
"""

import pytest
import subprocess
import shutil
from pathlib import Path


def test_missing_source_folder():
    """Test that vspace raises error when source folder doesn't exist."""
    test_dir = Path(__file__).parent / "MissingSource_Test"
    test_dir.mkdir(exist_ok=True)

    # Create vspace.in with non-existent source folder
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text("""
srcfolder /nonexistent/folder/that/does/not/exist
destfolder MissingSourceDest
samplemode grid

file earth.in
dSemi [1.0, 2.0, n2] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "does not exist" in error_output.lower() or "no such file" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_invalid_seed():
    """Test that vspace handles non-integer seed values."""
    test_dir = Path(__file__).parent / "InvalidSeed_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with invalid seed
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder InvalidSeedDest
samplemode random
seed not_a_number
randsize 10

file test.in
dSemi [1.0, 2.0, u] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred (either exception or invalid literal error)
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "invalid" in error_output.lower() or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_invalid_randsize():
    """Test that vspace handles non-positive randsize values."""
    test_dir = Path(__file__).parent / "InvalidRandsize_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with zero randsize
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder InvalidRandsizeDest
samplemode random
seed 42
randsize 0

file test.in
dSemi [1.0, 2.0, u] semi
""")

    # Run vspace - should fail or produce no output
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error or no trials created
    dest_dir = test_dir / "InvalidRandsizeDest"
    error_output = result.stdout + result.stderr

    # Either fails with error or creates empty destination
    if dest_dir.exists():
        trial_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
        assert len(trial_dirs) == 0, "Should not create trials with randsize=0"
    else:
        # Or fails with error message
        assert "error" in error_output.lower() or result.returncode != 0

    # Cleanup
    shutil.rmtree(test_dir)


def test_invalid_distribution_type():
    """Test that vspace rejects unknown distribution type characters."""
    test_dir = Path(__file__).parent / "InvalidDistribution_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with invalid distribution type 'z'
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder InvalidDistDest
samplemode random
seed 42
randsize 10

file test.in
dSemi [1.0, 2.0, z] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred
    error_output = result.stdout + result.stderr
    # May fail with index error, key error, or explicit validation error
    assert result.returncode != 0 or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_missing_angle_unit_for_sine():
    """Test that vspace requires sUnitAngle for sine distribution."""
    test_dir = Path(__file__).parent / "MissingAngleUnit_Test"
    test_dir.mkdir(exist_ok=True)

    # Create template WITHOUT sUnitAngle
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dInc 45.0\n")

    # Create vspace.in with sine distribution
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder MissingAngleDest
samplemode random
seed 42
randsize 10

file test.in
dInc [0, 90, s] inc
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred
    error_output = result.stdout + result.stderr
    # Should fail when searching for sUnitAngle
    assert result.returncode != 0 or "sunitangle" in error_output.lower() or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_negative_randsize():
    """Test that vspace handles negative randsize values."""
    test_dir = Path(__file__).parent / "NegativeRandsize_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with negative randsize
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder NegativeRandsizeDest
samplemode random
seed 42
randsize -10

file test.in
dSemi [1.0, 2.0, u] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
