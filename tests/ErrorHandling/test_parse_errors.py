"""
Tests for vspace input parsing errors.

This module tests that vspace properly handles malformed input syntax
and provides helpful error messages.
"""

import pytest
import subprocess
import shutil
from pathlib import Path


def test_malformed_bracket_syntax():
    """Test that vspace handles missing/unmatched brackets."""
    test_dir = Path(__file__).parent / "MalformedBracket_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with missing closing bracket
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder MalformedBracketDest
samplemode grid

file test.in
dSemi [1.0, 2.0, n2 semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred (likely index error from parsing)
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_wrong_number_of_values():
    """Test that vspace handles incorrect number of values in brackets."""
    test_dir = Path(__file__).parent / "WrongValueCount_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with only 2 values (should be 3)
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder WrongValueDest
samplemode grid

file test.in
dSemi [1.0, 2.0] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred (likely index error)
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_non_integer_grid_points():
    """Test that vspace handles non-integer grid point specifications."""
    test_dir = Path(__file__).parent / "NonIntegerGrid_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with float grid points (n3.5)
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder NonIntegerDest
samplemode grid

file test.in
dSemi [1.0, 2.0, n3.5] semi
""")

    # Run vspace - should fail or handle gracefully
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred (ValueError from int() conversion)
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "error" in error_output.lower() or "invalid literal" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


def test_invalid_cutoff_syntax():
    """Test that vspace handles malformed min/max cutoff syntax."""
    test_dir = Path(__file__).parent / "InvalidCutoff_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dSemi 1.0\n")

    # Create vspace.in with malformed cutoff (missing value)
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder InvalidCutoffDest
samplemode random
seed 42
randsize 10

file test.in
dSemi [0.0, 1.0, g, min] semi
""")

    # Run vspace - should fail
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    # Verify error occurred (likely ValueError from float conversion)
    error_output = result.stdout + result.stderr
    assert result.returncode != 0 or "error" in error_output.lower()

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
