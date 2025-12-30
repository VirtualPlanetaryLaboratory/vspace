"""Test option removal using 'rm' syntax."""

import subprocess
from pathlib import Path
import pytest


def test_option_removal_with_rm():
    """Test that options can be removed using 'rm' prefix."""
    test_dir = Path(__file__).parent / "OptionRemoval_Test"
    test_dir.mkdir(exist_ok=True)

    # Create template directory with a file containing multiple options
    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)

    template_file = template_dir / "earth.in"
    template_file.write_text("""sName earth
dMass -1.0
dRadius -1.0
dSemi -1.0
dEcc 0.0
dObliquity 23.5
""")

    # Create vspace input that removes dObliquity using rm syntax
    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""srcfolder {template_dir}
destfolder OptionRemovalDest
samplemode grid
file earth.in
dSemi [1.0, 2.0, n2] semi
rm dObliquity
""")

    # Run vspace with force flag to avoid interactive prompts
    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    # Check that trials were created
    dest_dir = test_dir / "OptionRemovalDest"
    assert dest_dir.exists()

    # Read one of the generated files
    trial_dirs = sorted([d for d in dest_dir.iterdir() if d.is_dir()])
    assert len(trial_dirs) == 2, f"Expected 2 trials, got {len(trial_dirs)}"

    trial_file = trial_dirs[0] / "earth.in"
    assert trial_file.exists()

    content = trial_file.read_text()

    # Verify dSemi was updated
    assert "dSemi 1.0" in content or "dSemi 2.0" in content

    # Verify dObliquity was commented out (removed)
    lines = content.split('\n')
    obliquity_commented = False
    for line in lines:
        if 'dObliquity' in line:
            assert line.strip().startswith('#'), f"dObliquity should be commented: {line}"
            obliquity_commented = True

    assert obliquity_commented, "dObliquity should be present but commented out"

    # Verify other options remain unchanged
    assert "dMass -1.0" in content
    assert "dRadius -1.0" in content


def test_multiple_options_removal():
    """Test removing multiple options simultaneously."""
    test_dir = Path(__file__).parent / "MultiOptionRemoval_Test"
    test_dir.mkdir(exist_ok=True)

    template_dir = test_dir / "template"
    template_dir.mkdir(exist_ok=True)

    template_file = template_dir / "test.in"
    template_file.write_text("""sName test
dOpt1 1.0
dOpt2 2.0
dOpt3 3.0
dOpt4 4.0
dOpt5 5.0
""")

    vspace_in = test_dir / "vspace.in"
    vspace_in.write_text(f"""srcfolder {template_dir}
destfolder MultiRemovalDest
samplemode grid
file test.in
dOpt1 [10, 20, n2] opt1
rm dOpt2
rm dOpt4
""")

    result = subprocess.run(
        ["vspace", "-f", "vspace.in"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"vspace failed: {result.stderr}"

    dest_dir = test_dir / "MultiRemovalDest"
    trial_dirs = sorted([d for d in dest_dir.iterdir() if d.is_dir()])
    trial_file = trial_dirs[0] / "test.in"
    content = trial_file.read_text()

    # dOpt1 should be updated
    assert "dOpt1 10" in content or "dOpt1 20" in content

    # dOpt2 and dOpt4 should be commented
    lines = content.split('\n')
    for line in lines:
        if 'dOpt2' in line or 'dOpt4' in line:
            assert line.strip().startswith('#'), f"Option should be commented: {line}"

    # dOpt3 and dOpt5 should be unchanged
    assert "dOpt3 3.0" in content
    assert "dOpt5 5.0" in content
