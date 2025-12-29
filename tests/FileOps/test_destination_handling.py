"""
Tests for destination folder handling and override behavior.

This module tests folder creation, force flag functionality, and cleanup
of bigplanet/multiplanet checkpoint files.
"""

import pytest
import subprocess
import shutil
from pathlib import Path


def test_destination_creation():
    """Test that vspace creates destination folder if it doesn't exist."""
    test_dir = Path(__file__).parent / "DestCreation_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dMass 1.0\n")

    # Ensure destination doesn't exist
    dest_dir = test_dir / "NewDestination"
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Create vspace.in
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder {dest_dir}
samplemode grid

file test.in
dMass [1.0, 2.0, n2] mass
""")

    # Run vspace
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    # Verify destination was created
    assert dest_dir.exists(), "Destination folder not created"
    assert dest_dir.is_dir(), "Destination is not a directory"

    # Verify trials were created
    trial_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
    assert len(trial_dirs) == 2, f"Expected 2 trials, got {len(trial_dirs)}"

    # Cleanup
    shutil.rmtree(test_dir)


def test_force_flag_bypasses_prompt():
    """Test that --force flag bypasses override prompt."""
    test_dir = Path(__file__).parent / "ForceFlag_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dMass 1.0\n")

    # Create vspace.in
    dest_dir = test_dir / "ForceDestination"
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder {dest_dir}
samplemode grid

file test.in
dMass [1.0, 2.0, n2] mass
""")

    # Run vspace first time to create destination
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"First vspace run failed: {result.stderr}"
    assert dest_dir.exists(), "Destination not created on first run"

    # Create a marker file to verify override
    marker_file = dest_dir / "marker.txt"
    marker_file.write_text("This should be deleted")

    # Run vspace again with --force flag (should not prompt)
    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=10  # Should complete quickly without waiting for input
    )

    assert result.returncode == 0, f"Second vspace run with -f failed: {result.stderr}"

    # Verify destination still exists but marker is gone (folder was recreated)
    assert dest_dir.exists(), "Destination folder missing after override"
    assert not marker_file.exists(), "Marker file still exists (folder not overridden)"

    # Verify new trials were created
    trial_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
    assert len(trial_dirs) == 2, f"Expected 2 trials after override, got {len(trial_dirs)}"

    # Cleanup
    shutil.rmtree(test_dir)


def test_cleanup_bpl_files():
    """Test that .bpl and checkpoint files are removed on override."""
    test_dir = Path(__file__).parent / "CleanupBpl_Test"
    test_dir.mkdir(exist_ok=True)

    # Create minimal template
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)
    (template_dir / "test.in").write_text("dMass 1.0\n")

    # Create vspace.in
    dest_name = "CleanupDest"
    dest_dir = test_dir / dest_name
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""
srcfolder {template_dir}
destfolder {dest_name}
samplemode grid

file test.in
dMass [1.0, 2.0, n2] mass
""")

    # Clean up any previous test runs
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Run vspace first time
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"First vspace run failed: {result.stderr}"

    # Create bigplanet/multiplanet checkpoint files
    # These files are created by bigplanet and multiplanet
    # Based on vspace.py lines 109-114 and 129-134
    bpl_file1 = test_dir / f"{dest_name}.bpl"
    bpl_file2 = test_dir / f".{dest_name}_bpl"
    bpl_file3 = test_dir / f".{dest_name}"

    bpl_file1.write_text("bigplanet checkpoint")
    bpl_file2.write_text("hidden bigplanet checkpoint")
    bpl_file3.write_text("hidden destination file")

    # Verify checkpoint files exist
    assert bpl_file1.exists(), "bpl file 1 not created"
    assert bpl_file2.exists(), "bpl file 2 not created"
    assert bpl_file3.exists(), "bpl file 3 not created"

    # Run vspace again with --force
    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Second vspace run failed: {result.stderr}"

    # Verify checkpoint files were removed
    assert not bpl_file1.exists(), f"{bpl_file1.name} not removed"
    assert not bpl_file2.exists(), f"{bpl_file2.name} not removed"
    assert not bpl_file3.exists(), f"{bpl_file3.name} not removed"

    # Verify destination was recreated
    assert dest_dir.exists(), "Destination folder missing"
    trial_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
    assert len(trial_dirs) == 2, f"Expected 2 trials, got {len(trial_dirs)}"

    # Cleanup
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
