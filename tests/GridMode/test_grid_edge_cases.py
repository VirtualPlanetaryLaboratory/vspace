"""
Tests for edge cases in grid mode sampling.

This module tests boundary conditions and special cases for grid generation.
"""

import pytest
import subprocess
import shutil
from pathlib import Path
import numpy as np


def test_single_point_grid():
    """Test grid with single value [1.0, 1.0, n1]."""
    test_dir = Path(__file__).parent / "SinglePoint_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "earth.in").write_text("dSemi 1.0\n")

    # Create vspace.in with single point
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder SinglePoint_Grid
samplemode grid

file earth.in
dSemi [1.0, 1.0, n1] semi
""")

    # Run vspace
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    # Verify output
    output_dir = test_dir / "SinglePoint_Grid"
    assert output_dir.exists(), "Output directory not created"

    # Should have exactly 1 trial directory
    trial_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
    assert len(trial_dirs) == 1, f"Expected 1 trial, got {len(trial_dirs)}"

    # Read the parameter value
    trial_dir = trial_dirs[0]
    earth_file = trial_dir / "earth.in"
    assert earth_file.exists(), "earth.in not created"

    contents = earth_file.read_text()
    lines = [line.strip() for line in contents.split('\n') if line.strip()]

    # Find dSemi value
    semi_value = None
    for line in lines:
        if line.startswith('dSemi'):
            semi_value = float(line.split()[1])
            break

    assert semi_value is not None, "dSemi not found in output"
    assert abs(semi_value - 1.0) < 1e-10, f"Expected dSemi=1.0, got {semi_value}"

    # Cleanup
    shutil.rmtree(test_dir)


def test_large_grid():
    """Test large grid [0, 100, n101] for performance and correctness."""
    test_dir = Path(__file__).parent / "LargeGrid_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "earth.in").write_text("dSemi 1.0\n")

    # Create vspace.in with large grid
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder LargeGrid
samplemode grid

file earth.in
dSemi [0, 100, n101] semi
""")

    # Run vspace with timeout and force flag
    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=60  # Should complete in <60 seconds
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    # Verify output
    output_dir = test_dir / "LargeGrid"
    assert output_dir.exists(), "Output directory not created"

    # Should have exactly 101 trial directories
    trial_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()])
    assert len(trial_dirs) == 101, f"Expected 101 trials, got {len(trial_dirs)}"

    # Check grid_list.dat
    grid_list = output_dir / "grid_list.dat"
    assert grid_list.exists(), "grid_list.dat not created"

    # Parse grid_list.dat
    with open(grid_list) as f:
        lines = f.readlines()

    # Skip header line (first line with "trial"), get data lines
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 101, f"Expected 101 data lines, got {len(data_lines)}"

    # Extract values and verify they're evenly spaced
    values = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 2:
            values.append(float(parts[1]))

    values = np.array(values)
    expected_values = np.linspace(0, 100, 101)

    # Verify values match expected grid
    assert len(values) == 101, f"Expected 101 values, got {len(values)}"
    assert np.allclose(values, expected_values, rtol=1e-10), "Grid values don't match expected linear spacing"

    # Verify first and last values
    assert abs(values[0] - 0.0) < 1e-10, f"First value should be 0.0, got {values[0]}"
    assert abs(values[-1] - 100.0) < 1e-10, f"Last value should be 100.0, got {values[-1]}"

    # Verify spacing is uniform
    diffs = np.diff(values)
    expected_spacing = 1.0  # (100-0)/(101-1) = 1.0
    assert np.allclose(diffs, expected_spacing, rtol=1e-10), f"Spacing not uniform: {diffs[:5]}...{diffs[-5:]}"

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
