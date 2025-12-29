import pathlib
import subprocess
import sys
import shutil


def test_gaussian_negative_sigma():
    """
    Test that Gaussian distribution with negative sigma produces error.

    This validates the bugfix on the sigmaerror branch (vspace.py lines 384-392)
    that prevents crashes when users specify negative standard deviation.
    """
    # Get current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = path / "NegativeSigma_Test"

    # Remove anything from previous tests
    if dir.exists():
        shutil.rmtree(dir)

    # Run vspace with negative sigma - should exit with error
    # We expect this to fail gracefully with error message
    result = subprocess.run(
        ["vspace", "vspace.in"],
        cwd=path,
        capture_output=True,
        text=True
    )

    # Note: Current implementation uses exit() without error code (bug).
    # This should be fixed to use sys.exit(1) or raise IOError during refactoring.
    # For now, we verify the error message was printed.

    # Verify error message was printed
    error_output = result.stdout + result.stderr
    assert "Standard deviation must be non-negative" in error_output, \
        "Error message should mention non-negative standard deviation requirement"

    # Verify the error mentions the correct parameter name
    assert "dSemi" in error_output, \
        "Error message should identify which parameter has the issue"

    # Verify no output directory was created (graceful failure)
    assert not dir.exists(), \
        "Output directory should not be created when input validation fails"


if __name__ == "__main__":
    test_gaussian_negative_sigma()
