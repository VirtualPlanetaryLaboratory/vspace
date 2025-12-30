# VSPACE Development Plan

**Repository:** vspace - Parameter sweep generator for VPLanet simulations
**Last Updated:** 2025-12-28
**Status:** Comprehensive review completed, improvement plan defined

---

## Executive Summary

The vspace repository generates parameter sweeps for VPLanet simulations by creating directory structures with modified input files. After thorough analysis, the code has significant style guideline violations, limited test coverage, and substantial opportunities for refactoring. This document provides a comprehensive plan to bring vspace into full compliance with project coding standards while ensuring scientific correctness through rigorous testing.

**Current State:**
- 1,218 lines in single monolithic `main()` function (target: <20 lines per function)
- 5 unit tests covering ~40% of functionality (target: 30+ tests, >90% coverage)
- Extensive naming convention violations (Hungarian notation not applied)
- Substantial code duplication between grid and random modes

**Improvement Strategy:**
1. **Phase 1 (4 weeks)**: Comprehensive testing - achieve >90% coverage before refactoring
2. **Phase 2 (5 weeks)**: Modular refactoring - decompose into small, orthogonal functions
3. **Phase 3 (2 weeks)**: Style compliance - apply Hungarian notation, clean up code
4. **Phase 4 (2 weeks)**: Enhanced testing - edge cases, performance, integration
5. **Phase 5 (2 weeks)**: Hyak module - assess relevance and refactor if retained
6. **Phase 6 (2 weeks)**: Documentation and release preparation

**Total Timeline:** 17 weeks

---

## Current State Analysis

### Repository Structure

```
vspace/
├── vspace/
│   ├── __init__.py (15 lines)
│   ├── vspace.py (1,218 lines) ← CRITICAL: Monolithic main() function
│   ├── vspace_hyak.py (363 lines)
│   ├── hyak.py (34 lines)
│   └── vspace_version.py (auto-generated)
├── tests/
│   ├── Vspace_Explicit/ (1 test)
│   ├── Vspace_Linear/ (1 test)
│   ├── Vspace_Log/ (1 test)
│   ├── Vspace_PreDefPrior_npy/ (1 test)
│   └── Vspace_PreDefPrior_txt/ (1 test)
├── docs/ (Sphinx documentation)
└── setup.py
```

### Code Quality Issues

#### Critical Violations

1. **Function Length Violation (SEVERE)**
   - **[vspace.py:36-1218](vspace/vspace.py#L36-L1218)** - `main()` function is **1,182 lines**
   - Violates <20 line requirement by **59x**
   - Contains all parsing, validation, sampling, and file generation logic
   - Impossible to unit test individual components
   - Must be refactored into 50-60 smaller functions

2. **Function Naming Violations**
   - `SearchAngleUnit()` → should be `fsSearchAngleUnit()` (returns string)
   - `main()` → should be `fnMain()` (returns None)
   - `parseInput()` → should be `ftParseInput()` (returns tuple)
   - `makeCommandList()` → should be `fnMakeCommandList()` (returns None)
   - `makeHyakVPlanetPBS()` → should be `fnMakeHyakVplanetPBS()` (returns None)

3. **Variable Naming Violations (Hungarian Notation Missing)**

   | Current | Required | Type |
   |---------|----------|------|
   | `lines` | `listLines` | list |
   | `fnum` | `iFileNum` | int |
   | `flist` | `listFiles` | list |
   | `iter_var` | `listIterVar` | list |
   | `iter_file` | `listIterFile` | list |
   | `iter_name` | `listIterName` | list |
   | `prefix` | `listPrefix` | list |
   | `prior_files` | `listPriorFiles` | list |
   | `prior_samples` | `listPriorSamples` | list |
   | `prior_indicies` | `listPriorIndices` | list (also fix typo) |
   | `numtry` | `iNumTry` | int |
   | `numvars` | `iNumVars` | int |
   | `angUnit` | `sAngUnit` | string |
   | `mode` | `iMode` | int |
   | `randsize` | `iRandSize` | int |
   | `src` | `sSrcFolder` | string |
   | `dest` | `sDestFolder` | string |
   | `trial` | `sTrialName` | string |

4. **Code Duplication (SEVERE)**
   - Lines 763-827: File copying logic (no variable parameters)
   - Lines 838-999: Grid mode file generation (161 lines)
   - Lines 1001-1159: Random mode file generation (158 lines)
   - **~85% overlap between grid and random modes**
   - Gaussian and log-normal sampling nearly identical (lines 380-520)
   - File validation and option matching repeated 3+ times

5. **Abbreviations <8 Characters**
   - `src` → `source` (then prefix as `sSource`)
   - `dest` → `destination` (then `sDestination`)
   - `tup` → `tuple` (avoid as variable name, use `tValues`)
   - `spl` → `split` (then `listSplit`)

#### Moderate Issues

6. **Poor Separation of Concerns**
   - Input parsing, validation, business logic, and I/O all in single function
   - No data structures to represent parsed configuration
   - Direct file I/O interleaved with algorithm logic
   - Makes testing individual components impossible

7. **Error Handling Inconsistencies**
   - Most errors use `raise IOError()` with good messages (positive)
   - Some use `print()` + `exit()` (lines 392, 775-776) - should raise exceptions
   - Missing validation for some edge cases

8. **Magic Numbers and Strings**
   - String literals repeated: "srcfolder", "sSrcFolder", "destfolder", "sDestFolder"
   - No constants for mode values (0=grid, 1=random)
   - Distribution type characters ('n', 'l', 'u', 't', 'g', 'G', 's', 'c', 'p') not centralized

9. **Dead and Debug Code**
   - Lines 1186-1214: Entire block wrapped in `if False:` - should be removed
   - Lines 430-438, 506-514: Commented code with "wtf???" comment
   - Lines 1022-1024: `import pdb; pdb.set_trace()` in production
   - Line 6: Commented import statement

10. **Excessive Comments**
    - Lines 82-187: Comments explaining every line of parsing logic
    - Comments like "# Megan's Addition" (lines 71-75, 190-219) indicate unintegrated contributions
    - Code should be self-documenting through clear names

### Test Coverage Analysis

#### Existing Tests (5 total, ~40% coverage)

1. **test_vspace_linear.py**
   - **Coverage**: Linear grid spacing with n-point syntax `[1.0, 2.0, n11]`
   - **Validates**: 11 semi-major axis values
   - **Limitation**: Only tests single parameter

2. **test_vspace_log.py**
   - **Coverage**: Logarithmic grid spacing `[1.0, 1000.0, l10]`
   - **Validates**: 10 log-spaced values
   - **Limitation**: Only tests single parameter

3. **test_vspace_explicit.py**
   - **Coverage**: Explicit step spacing `[1.0, 2.0, 0.1]`
   - **Validates**: 11 values with 0.1 spacing
   - **Limitation**: Only tests single parameter

4. **test_vspace_predefprior_npy.py**
   - **Coverage**: Pre-defined priors from .npy file, column selection, correlation preservation
   - **Validates**: Sample count, value ranges, row relationships
   - **Strength**: Most comprehensive existing test

5. **test_vspace_predefprior_txt.py**
   - **Coverage**: Pre-defined priors from ASCII file
   - **Validates**: Similar to .npy version

#### Critical Coverage Gaps

**Random Distribution Sampling (0% coverage):**
- ❌ Uniform distribution (`u`) - lines 523-537
- ❌ Log-uniform distribution (`t`) - lines 540-569
- ❌ Gaussian distribution (`g`) - lines 380-444 **[CRITICAL - recent bugfix untested!]**
- ❌ Gaussian with min/max cutoffs - lines 393-429
- ❌ Log-normal distribution (`G`) - lines 460-520
- ❌ Log-normal with cutoffs - lines 469-505
- ❌ Uniform sine distribution (`s`) - lines 571-615
- ❌ Uniform cosine distribution (`c`) - lines 617-661

**Grid Mode (limited coverage):**
- ❌ Multi-parameter sweeps (cartesian product)
- ❌ Multi-file parameter variations
- ❌ Negative value logarithmic spacing
- ❌ Edge cases: single value, large grids
- ❌ Directory naming with multiple parameters

**File Operations (0% coverage):**
- ❌ Source folder validation
- ❌ Destination folder creation/override
- ❌ Force flag (`-f`) behavior
- ❌ Template file reading
- ❌ Option replacement in existing files
- ❌ Option addition (not in template)
- ❌ Option removal via `rm` syntax
- ❌ Multiple .in file handling
- ❌ Home directory expansion (`~`)

**Output Validation (minimal coverage):**
- ❌ grid_list.dat format and content
- ❌ rand_list.dat format and content
- ❌ Histogram generation (random mode)
- ❌ PriorIndicies.json generation

**Error Handling (0% coverage):**
- ❌ Missing source folder
- ❌ Invalid seed/randsize
- ❌ Invalid distribution type
- ❌ Negative sigma in Gaussian
- ❌ Missing angle units for sine/cosine
- ❌ Malformed input syntax

**Hyak Module (0% coverage):**
- ❌ vspace_hyak.py has zero tests
- ❌ Unknown if this module is still in use

---

## Development Plan

### Phase 1: Comprehensive Testing (Weeks 1-4, CRITICAL PRIORITY)

**Objective:** Achieve >90% test coverage before refactoring to ensure behavior preservation.

**Rationale:** The code works but is poorly structured. We must document current behavior through tests before making changes. This follows "make the change easy, then make the easy change."

#### Week 1: Random Distribution Tests (Priority 1)

Create `tests/RandomDistributions/` directory with fixtures and utilities:

**Infrastructure:**
- `fixtures/templates/` - Minimal vplanet .in files
- `fixtures/inputs/` - Sample vspace.in files
- `test_utils.py` - Shared utilities:
  - `fnCreateTestTemplate()` - Generate .in files
  - `fnRunVspace()` - Execute vspace with error capture
  - `flistParseOutputList()` - Parse grid_list.dat/rand_list.dat
  - `fbValidateDirectories()` - Check directory structure
  - `fdaExtractParameterValues()` - Extract values from .in files

**Tests to implement:**

1. **test_uniform.py** (lines 523-537)
   ```python
   def test_uniform_basic():
       """Uniform distribution [1.0, 2.0, u] with seed=42, randsize=100."""
       # Verify all values in [1.0, 2.0]
       # Check mean ≈ 1.5 (±0.1)
       # Check std ≈ 0.289 (±0.05)
       # Validate rand_list.dat format
       # Verify histogram generated
   ```

2. **test_loguniform.py** (lines 540-569)
   ```python
   def test_loguniform_positive():
       """Log-uniform [1.0, 100.0, t]."""

   def test_loguniform_negative():
       """Log-uniform [-100.0, -1.0, t] - tests line 544-554."""
   ```

3. **test_gaussian.py** (lines 380-444) **HIGHEST PRIORITY**
   ```python
   def test_gaussian_basic():
       """Gaussian [0.0, 1.0, g] - standard normal."""

   def test_gaussian_negative_sigma():
       """Gaussian [0.0, -1.0, g] - should raise error (lines 384-392)."""
       # Tests sigmaerror branch bugfix - CURRENTLY UNTESTED!

   def test_gaussian_min_cutoff():
       """Gaussian [0.0, 1.0, g, min-2.0] - resampling logic."""

   def test_gaussian_max_cutoff():
       """Gaussian [0.0, 1.0, g, max2.0]."""

   def test_gaussian_both_cutoffs():
       """Gaussian [0.0, 1.0, g, min-1.0, max1.0]."""
   ```

4. **test_lognormal.py** (lines 460-520)
   ```python
   def test_lognormal_basic():
       """Log-normal [0.0, 1.0, G]."""

   def test_lognormal_cutoffs():
       """All cutoff variants like Gaussian."""
   ```

5. **test_seed_reproducibility.py**
   ```python
   def test_seed_reproduces_values():
       """Same seed produces identical random samples."""
       # Run twice with seed=42
       # Verify bit-identical outputs
   ```

**Deliverable:** 10-12 tests, coverage of lines 380-569 (random distributions)

#### Week 2: Trigonometric & Grid Tests

**Random mode (continued):**

6. **test_sine.py** (lines 571-615)
   ```python
   def test_sine_degrees():
       """Sine [0, 90, s] with sUnitAngle degrees."""

   def test_sine_radians():
       """Sine [0, 1.57, s] with sUnitAngle radians."""
   ```

7. **test_cosine.py** (lines 617-661)
   ```python
   def test_cosine_degrees():
       """Cosine [0, 90, c]."""

   def test_cosine_radians():
       """Cosine [0, 1.57, c]."""
   ```

**Grid mode expansion:**

Create `tests/GridMode/` directory:

8. **test_grid_multi_parameter.py**
   ```python
   def test_two_parameters_cartesian():
       """dSemi [1, 2, n3] and dEcc [0, 0.2, n3] → 9 trials."""
       # Verify 9 directories created
       # Check all 9 combinations present

   def test_three_parameters():
       """3 parameters → 8 trials (2x2x2)."""
   ```

9. **test_grid_negative_log.py**
   ```python
   def test_negative_log_spacing():
       """[-100, -1, l3] - tests lines 339-355."""
   ```

10. **test_grid_edge_cases.py**
    ```python
    def test_single_point_grid():
        """[1.0, 1.0, n1] - single value."""

    def test_large_grid():
        """[0, 100, n101] - performance test."""
    ```

**Deliverable:** 8-10 additional tests, grid mode coverage complete

#### Week 3: File Operations & Integration

Create `tests/FileOperations/` directory:

11. **test_file_discovery.py**
    ```python
    def test_source_folder_validation():
        """Non-existent srcfolder raises IOError."""

    def test_multiple_in_files():
        """srcfolder with earth.in, sun.in, vpl.in."""
    ```

12. **test_option_manipulation.py**
    ```python
    def test_option_replacement():
        """Replacing existing option in template."""

    def test_option_addition():
        """Adding option not in template."""

    def test_option_removal():
        """rm syntax to comment out option."""
    ```

13. **test_destination_handling.py**
    ```python
    def test_destination_creation():
        """Creates destination folder if doesn't exist."""

    def test_force_flag():
        """--force bypasses override prompt."""

    def test_cleanup_bpl_files():
        """Removes .bpl and checkpoint files on override."""
    ```

Create `tests/Integration/` directory:

14. **test_end_to_end_grid.py**
    ```python
    def test_realistic_grid_sweep():
        """Multi-file, multi-parameter grid mode."""
        # earth.in: dSemi, dEcc
        # sun.in: dMass
        # Validate all outputs
    ```

15. **test_end_to_end_random.py**
    ```python
    def test_realistic_random_sweep():
        """Multi-file, multi-distribution random mode."""
    ```

**Deliverable:** 10-12 tests, file operations and integration coverage

#### Week 4: Error Handling & Hyak

Create `tests/ErrorHandling/` directory:

16. **test_validation_errors.py**
    ```python
    def test_missing_source_folder():
    def test_invalid_seed():
    def test_invalid_randsize():
    def test_randsize_without_random_mode():
    def test_negative_sigma():  # Validates sigmaerror fix
    def test_invalid_distribution_type():
    def test_missing_angle_unit():
    ```

17. **test_parse_errors.py**
    ```python
    def test_malformed_bracket_syntax():
    def test_wrong_number_of_values():
    def test_non_integer_grid_points():
    def test_invalid_cutoff_syntax():
    ```

Create `tests/Hyak/` directory (if module is actively used):

18. **test_vspace_hyak.py**
    ```python
    def test_parse_input():
    def test_make_command_list():
    def test_make_pbs_script():
    ```

**Deliverable:** 15-20 error handling tests, Hyak tests if needed

**Phase 1 Complete When:**
- ✅ ≥30 tests passing
- ✅ All distribution types tested
- ✅ Coverage ≥90% on vspace.py
- ✅ sigmaerror branch validated
- ✅ All tests pass Python 3.9-3.14, macOS + Linux
- ✅ All tests run in <30 seconds total

---

### Phase 2: Modular Refactoring (Weeks 5-9, HIGH PRIORITY)

**Objective:** Decompose vspace.py into small, orthogonal, single-purpose functions.

**Constraint:** All Phase 1 tests must pass throughout refactoring.

**Strategy:** Red-Green-Refactor - extract functions incrementally, run tests after each change.

#### Week 5: Data Structures & Parser

**Step 1: Create data structures module**

`vspace/dataStructures.py`:

```python
"""Data structures for vspace configuration."""
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np

@dataclass
class VspaceConfig:
    """Configuration parsed from vspace input file."""
    sSrcFolder: str
    sDestFolder: str
    sTrialName: str = "default"
    iMode: int = 0  # 0=grid, 1=random
    iSeed: Optional[int] = None
    iRandSize: int = 0
    sAngleUnit: str = ""
    listFiles: List[str] = None
    listParameters: List['ParameterSpec'] = None

    def __post_init__(self):
        if self.listFiles is None:
            self.listFiles = []
        if self.listParameters is None:
            self.listParameters = []

@dataclass
class ParameterSpec:
    """Specification for a single parameter to vary."""
    sName: str
    sFile: str  # Which .in file contains this parameter
    sPrefix: str  # Directory name prefix
    sDistribution: str  # 'n', 'l', 'u', 't', 'g', 'G', 's', 'c', 'p'
    daValues: np.ndarray  # Generated samples/grid
    dLow: float
    dHigh: float
    dThird: float  # Spacing, sigma, or column number
    dictOptions: Dict = None  # Cutoffs, prior info, etc.

    def __post_init__(self):
        if self.dictOptions is None:
            self.dictOptions = {}
```

**Step 2: Create parser module**

`vspace/parser.py` (target: ~150 lines, 10-12 functions):

```python
"""Input file parsing for vspace."""

def fParseConfigFile(sFilePath: str) -> VspaceConfig:
    """
    Parse vspace input file.

    Returns VspaceConfig object with all settings.
    Target: 15 lines (orchestration only).
    """
    with open(sFilePath) as file:
        listLines = file.readlines()

    config = VspaceConfig()
    fnParseGlobalSettings(listLines, config)
    fnParseFileList(listLines, config)
    fnParseParameters(listLines, config)
    return config

def fnParseGlobalSettings(listLines: List[str], config: VspaceConfig) -> None:
    """Parse srcfolder, destfolder, mode, seed, etc. Target: <20 lines."""
    for sLine in listLines:
        listWords = sLine.split()
        if not listWords:
            continue
        sKeyword = listWords[0].lower()

        if sKeyword in ['ssrcfolder', 'srcfolder']:
            config.sSrcFolder = fsExpandPath(listWords[1])
        elif sKeyword in ['sdestfolder', 'destfolder']:
            config.sDestFolder = fsExpandPath(listWords[1])
        elif sKeyword in ['strialname', 'trialname']:
            config.sTrialName = listWords[1]
        # ... etc (10-15 more lines)

def fnParseFileList(listLines: List[str], config: VspaceConfig) -> None:
    """Extract .in file names. Target: <10 lines."""
    for sLine in listLines:
        listWords = sLine.split()
        if not listWords:
            continue
        if listWords[0].lower() in ['sbodyfile', 'sprimaryfile', 'file']:
            config.listFiles.append(listWords[1])

def fnParseParameters(listLines: List[str], config: VspaceConfig) -> None:
    """Parse bracketed parameter definitions. Target: <20 lines."""
    iCurrentFile = -1
    for i, sLine in enumerate(listLines):
        if fbIsFileLine(sLine):
            iCurrentFile += 1
        elif fbIsParameterLine(sLine):
            param = fParseParameterSpec(sLine, config.listFiles[iCurrentFile],
                                        config.iMode, config.iRandSize)
            config.listParameters.append(param)

def fbIsParameterLine(sLine: str) -> bool:
    """Check if line contains parameter definition. Target: 1 line."""
    return '[' in sLine and ']' in sLine

def fParseParameterSpec(sLine: str, sFile: str, iMode: int,
                        iRandSize: int) -> ParameterSpec:
    """
    Parse single parameter line into ParameterSpec.
    Target: <20 lines.
    """
    import re
    listParts = re.split(r'[\[\]]', sLine)
    sName = sLine.split()[0]
    listValues = [s.strip() for s in listParts[1].split(',')]
    sPrefix = listParts[2].strip()

    # Create ParameterSpec (values filled in later by samplers)
    param = ParameterSpec(
        sName=sName,
        sFile=sFile,
        sPrefix=sPrefix,
        sDistribution=listValues[2][0],
        daValues=np.array([]),
        dLow=float(listValues[0]),
        dHigh=float(listValues[1]),
        dThird=0.0  # Depends on distribution
    )

    fnParseDistributionOptions(listValues, param, iMode)
    return param

def fnParseDistributionOptions(listValues: List[str], param: ParameterSpec,
                                iMode: int) -> None:
    """Parse distribution-specific options (cutoffs, etc.). Target: <20 lines."""
    # Extract min/max cutoffs for Gaussian
    # Extract column number for predefined priors
    # Set dThird appropriately
    pass

def fsExpandPath(sPath: str) -> str:
    """Expand ~ in path. Target: 2 lines."""
    import os
    return os.path.expanduser(sPath) if '~' in sPath else sPath
```

**Estimated lines eliminated from main():** ~250 lines

#### Week 6: Sampling Module

`vspace/samplers.py` (target: ~180 lines, 12-15 functions):

```python
"""Distribution sampling functions for vspace."""

def fdaGenerateLinearGrid(dLow: float, dHigh: float, iPoints: int) -> np.ndarray:
    """Generate linear grid. Target: 1 line."""
    return np.linspace(dLow, dHigh, iPoints)

def fdaGenerateLogGrid(dLow: float, dHigh: float, iPoints: int) -> np.ndarray:
    """
    Generate logarithmic grid. Handles negative values.
    Target: 5 lines.
    """
    if dLow < 0:
        return -np.logspace(np.log10(-dLow), np.log10(-dHigh), iPoints)
    return np.logspace(np.log10(dLow), np.log10(dHigh), iPoints)

def fdaGenerateExplicitGrid(dLow: float, dHigh: float, dInterval: float) -> np.ndarray:
    """Generate grid with explicit interval. Target: 1 line."""
    return np.arange(dLow, dHigh + dInterval, dInterval)

def fdaSampleUniform(dLow: float, dHigh: float, iSize: int) -> np.ndarray:
    """Sample uniform distribution. Target: 1 line."""
    return np.random.uniform(low=dLow, high=dHigh, size=iSize)

def fdaSampleLogUniform(dLow: float, dHigh: float, iSize: int) -> np.ndarray:
    """
    Sample log-uniform distribution. Handles negative values.
    Target: 6 lines.
    """
    if dLow < 0:
        return -np.power(10, np.random.uniform(
            low=np.log10(-dLow), high=np.log10(-dHigh), size=iSize))
    return np.power(10, np.random.uniform(
        low=np.log10(dLow), high=np.log10(dHigh), size=iSize))

def fdaSampleGaussian(dMean: float, dSigma: float, iSize: int,
                      dMinCutoff: Optional[float] = None,
                      dMaxCutoff: Optional[float] = None) -> np.ndarray:
    """
    Sample Gaussian distribution with optional cutoffs.
    Resamples values outside cutoffs.
    Target: 15 lines.
    """
    if dSigma < 0:
        raise ValueError(f"Standard deviation must be non-negative, got {dSigma}")

    daArray = np.random.normal(loc=dMean, scale=dSigma, size=iSize)

    if dMinCutoff is None and dMaxCutoff is None:
        return daArray

    for i in range(iSize):
        while fbOutsideCutoffs(daArray[i], dMinCutoff, dMaxCutoff):
            daArray[i] = np.random.normal(loc=dMean, scale=dSigma, size=1)[0]

    return daArray

def fbOutsideCutoffs(dValue: float, dMin: Optional[float],
                     dMax: Optional[float]) -> bool:
    """Check if value outside cutoff range. Target: 5 lines."""
    if dMin is not None and dValue < dMin:
        return True
    if dMax is not None and dValue > dMax:
        return True
    return False

def fdaSampleLogNormal(dMean: float, dSigma: float, iSize: int,
                       dMinCutoff: Optional[float] = None,
                       dMaxCutoff: Optional[float] = None) -> np.ndarray:
    """
    Sample log-normal distribution with optional cutoffs.
    Target: 15 lines (similar to Gaussian).
    """
    daArray = np.random.lognormal(mean=dMean, sigma=dSigma, size=iSize)

    if dMinCutoff is None and dMaxCutoff is None:
        return daArray

    for i in range(iSize):
        while fbOutsideCutoffs(daArray[i], dMinCutoff, dMaxCutoff):
            daArray[i] = np.random.lognormal(mean=dMean, sigma=dSigma, size=1)[0]

    return daArray

def fdaSampleSine(dLow: float, dHigh: float, iSize: int, sAngleUnit: str) -> np.ndarray:
    """
    Sample uniform in sine of angle.
    Target: 8 lines.
    """
    if sAngleUnit.startswith('d') or sAngleUnit.startswith('D'):
        # Degrees
        dLowRad = dLow * np.pi / 180.0
        dHighRad = dHigh * np.pi / 180.0
        return np.arcsin(np.random.uniform(
            low=np.sin(dLowRad), high=np.sin(dHighRad), size=iSize)) * 180.0 / np.pi
    elif sAngleUnit.startswith('r') or sAngleUnit.startswith('R'):
        # Radians
        return np.arcsin(np.random.uniform(
            low=np.sin(dLow), high=np.sin(dHigh), size=iSize))
    else:
        raise ValueError(f"Invalid angle unit: {sAngleUnit}")

def fdaSampleCosine(dLow: float, dHigh: float, iSize: int, sAngleUnit: str) -> np.ndarray:
    """
    Sample uniform in cosine of angle.
    Target: 8 lines (similar to sine).
    """
    if sAngleUnit.startswith('d') or sAngleUnit.startswith('D'):
        dLowRad = dLow * np.pi / 180.0
        dHighRad = dHigh * np.pi / 180.0
        return np.arccos(np.random.uniform(
            low=np.cos(dLowRad), high=np.cos(dHighRad), size=iSize)) * 180.0 / np.pi
    elif sAngleUnit.startswith('r') or sAngleUnit.startswith('R'):
        return np.arccos(np.random.uniform(
            low=np.cos(dLow), high=np.cos(dHigh), size=iSize))
    else:
        raise ValueError(f"Invalid angle unit: {sAngleUnit}")

def fdaSamplePredefinedPrior(sPriorFile: str, sFileType: str, iColumn: int,
                              listPriorSamples: List) -> np.ndarray:
    """
    Extract column from predefined prior samples.
    Target: 3 lines.
    """
    iColIndex = iColumn - 1
    return np.array([sample[iColIndex] for sample in listPriorSamples])

def fnPopulateParameterArrays(config: VspaceConfig) -> None:
    """
    Generate sample arrays for all parameters.
    Target: 15 lines (dispatches to appropriate sampler).
    """
    for param in config.listParameters:
        if config.iMode == 0:  # Grid mode
            param.daValues = fdaGenerateGrid(param)
        else:  # Random mode
            param.daValues = fdaSampleRandom(param, config)

def fdaGenerateGrid(param: ParameterSpec) -> np.ndarray:
    """Dispatch to appropriate grid generator. Target: 10 lines."""
    if param.sDistribution == 'n':
        return fdaGenerateLinearGrid(param.dLow, param.dHigh, int(param.dThird))
    elif param.sDistribution == 'l':
        return fdaGenerateLogGrid(param.dLow, param.dHigh, int(param.dThird))
    else:  # Explicit interval
        return fdaGenerateExplicitGrid(param.dLow, param.dHigh, param.dThird)

def fdaSampleRandom(param: ParameterSpec, config: VspaceConfig) -> np.ndarray:
    """Dispatch to appropriate random sampler. Target: 18 lines."""
    sDistrib = param.sDistribution
    if sDistrib == 'u':
        return fdaSampleUniform(param.dLow, param.dHigh, config.iRandSize)
    elif sDistrib == 't':
        return fdaSampleLogUniform(param.dLow, param.dHigh, config.iRandSize)
    elif sDistrib == 'g':
        return fdaSampleGaussian(param.dLow, param.dThird, config.iRandSize,
                                 param.dictOptions.get('dMinCutoff'),
                                 param.dictOptions.get('dMaxCutoff'))
    elif sDistrib == 'G':
        return fdaSampleLogNormal(param.dLow, param.dThird, config.iRandSize,
                                  param.dictOptions.get('dMinCutoff'),
                                  param.dictOptions.get('dMaxCutoff'))
    elif sDistrib == 's':
        return fdaSampleSine(param.dLow, param.dHigh, config.iRandSize, config.sAngleUnit)
    elif sDistrib == 'c':
        return fdaSampleCosine(param.dLow, param.dHigh, config.iRandSize, config.sAngleUnit)
    elif sDistrib == 'p':
        return fdaSamplePredefinedPrior(param.dictOptions['sPriorFile'],
                                        param.dictOptions['sFileType'],
                                        int(param.dThird),
                                        param.dictOptions['listSamples'])
    else:
        raise ValueError(f"Unknown distribution type: {sDistrib}")
```

**Estimated lines eliminated from main():** ~350 lines

#### Week 7: File Generation Module

`vspace/fileWriter.py` (target: ~200 lines, 15-20 functions):

```python
"""File generation for vspace trials."""

def fnGenerateAllTrials(config: VspaceConfig) -> None:
    """
    Generate all trial directories and files.
    Target: 5 lines (dispatches to grid or random).
    """
    if config.iMode == 0:
        fnGenerateGridTrials(config)
    else:
        fnGenerateRandomTrials(config)

def fnGenerateGridTrials(config: VspaceConfig) -> None:
    """
    Generate grid mode trials.
    Target: 15 lines (creates product, writes each).
    """
    import itertools

    listArrays = [param.daValues for param in config.listParameters]
    listCombinations = list(itertools.product(*listArrays))

    with open(os.path.join(config.sDestFolder, "grid_list.dat"), 'w') as file:
        fnWriteGridHeader(file, config)
        for iTrial, tValues in enumerate(listCombinations):
            sTrialDir = fsFormatGridDirectoryName(config, tValues, iTrial)
            fnWriteGridListLine(file, sTrialDir, tValues)
            fnWriteTrialFiles(config, sTrialDir, tValues)

def fnGenerateRandomTrials(config: VspaceConfig) -> None:
    """
    Generate random mode trials.
    Target: 12 lines.
    """
    with open(os.path.join(config.sDestFolder, "rand_list.dat"), 'w') as file:
        fnWriteRandHeader(file, config)
        for iTrial in range(config.iRandSize):
            tValues = tuple(param.daValues[iTrial] for param in config.listParameters)
            sTrialDir = fsFormatRandDirectoryName(config.sTrialName, iTrial, config.iRandSize)
            fnWriteRandListLine(file, sTrialDir, tValues)
            fnWriteTrialFiles(config, sTrialDir, tValues)

    fnWriteHistograms(config)
    fnWritePriorIndices(config)

def fnWriteTrialFiles(config: VspaceConfig, sTrialDir: str,
                      tValues: tuple) -> None:
    """
    Write all .in files for one trial.
    This eliminates duplication between grid and random modes.
    Target: 12 lines.
    """
    sFullPath = os.path.join(config.sDestFolder, sTrialDir)
    os.makedirs(sFullPath, exist_ok=True)

    for sFileName in config.listFiles:
        listLines = flistReadTemplateFile(config.sSrcFolder, sFileName)
        dictReplacements = fdictGetReplacements(config, sFileName, tValues)
        listModified = flistApplyReplacements(listLines, dictReplacements)
        fnWriteFile(os.path.join(sFullPath, sFileName), listModified)

def fdictGetReplacements(config: VspaceConfig, sFileName: str,
                         tValues: tuple) -> Dict[str, float]:
    """
    Build parameter->value mapping for this file and trial.
    Target: 8 lines.
    """
    dictReplace = {}
    for i, param in enumerate(config.listParameters):
        if param.sFile == sFileName:
            dictReplace[param.sName] = tValues[i]
    return dictReplace

def flistApplyReplacements(listLines: List[str],
                           dictReplacements: Dict[str, float]) -> List[str]:
    """
    Apply parameter replacements to template lines.
    Target: 15 lines.
    """
    listResult = []
    setReplaced = set()

    for sLine in listLines:
        listWords = sLine.split()
        if listWords and listWords[0] in dictReplacements:
            listResult.append(f"{listWords[0]} {dictReplacements[listWords[0]]}\n")
            setReplaced.add(listWords[0])
        else:
            listResult.append(sLine)

    # Add any parameters not found in template
    for sParam, dValue in dictReplacements.items():
        if sParam not in setReplaced:
            listResult.append(f"\n{sParam} {dValue}\n")

    return listResult

def fsFormatGridDirectoryName(config: VspaceConfig, tValues: tuple,
                               iTrial: int) -> str:
    """Format directory name for grid trial. Target: 10 lines."""
    sParts = [config.sTrialName]
    for i, param in enumerate(config.listParameters):
        iIndex = np.where(param.daValues == tValues[i])[0][0]
        iDigits = len(str(len(param.daValues) - 1))
        sParts.append(f"{param.sPrefix}{iIndex:0{iDigits}d}")
    return "_".join(sParts)

def fsFormatRandDirectoryName(sTrialName: str, iTrial: int, iTotalTrials: int) -> str:
    """Format directory name for random trial. Target: 2 lines."""
    iDigits = len(str(iTotalTrials - 1))
    return f"{sTrialName}rand_{iTrial:0{iDigits}d}"

# Additional functions: fnWriteGridHeader, fnWriteRandHeader, fnWriteHistograms, etc.
# Each <20 lines
```

**Estimated lines eliminated from main():** ~400 lines

#### Week 8: Utilities & Validation

`vspace/validators.py` (target: ~80 lines, 6-8 functions):

```python
"""Configuration validation for vspace."""

def fnValidateConfig(config: VspaceConfig) -> None:
    """
    Validate parsed configuration.
    Target: 8 lines (calls specific validators).
    """
    fnValidateSourceFolder(config.sSrcFolder)
    fnValidateDestinationFolder(config.sDestFolder)
    fnValidateFiles(config.sSrcFolder, config.listFiles)
    fnValidateMode(config.iMode, config.iRandSize)
    fnValidateParameters(config.listParameters)

def fnValidateSourceFolder(sSrcFolder: str) -> None:
    """Verify source folder exists. Target: 3 lines."""
    if not os.path.exists(sSrcFolder):
        raise IOError(f"Source folder '{sSrcFolder}' does not exist")

def fnValidateDestinationFolder(sDestFolder: str) -> None:
    """Verify destination parent exists. Target: 7 lines."""
    if '/' in sDestFolder:
        sParent = '/'.join(sDestFolder.split('/')[:-1])
        if not os.path.exists(sParent):
            raise IOError(f"Destination parent '{sParent}' does not exist")

def fnValidateFiles(sSrcFolder: str, listFiles: List[str]) -> None:
    """Verify all template files exist. Target: 5 lines."""
    if not listFiles:
        raise IOError("No files specified in configuration")
    for sFile in listFiles:
        if not os.path.exists(os.path.join(sSrcFolder, sFile)):
            raise IOError(f"Template file '{sFile}' not found in '{sSrcFolder}'")

def fnValidateMode(iMode: int, iRandSize: int) -> None:
    """Validate mode and randsize consistency. Target: 4 lines."""
    if iMode == 1 and iRandSize == 0:
        raise IOError("Random mode requires iNumTrials > 0")

def fnValidateParameters(listParams: List[ParameterSpec]) -> None:
    """Validate parameter specifications. Target: 15 lines."""
    for param in listParams:
        if param.sDistribution in ['g', 'G'] and param.dThird < 0:
            raise ValueError(f"Standard deviation must be non-negative for {param.sName}")
        # Additional validations...
```

`vspace/utils.py` (target: ~60 lines, 5-7 functions):

```python
"""Utility functions for vspace."""

def fsSearchAngleUnit(sSrcFolder: str, listFiles: List[str]) -> str:
    """
    Search template files for angle unit.
    Target: 8 lines.
    """
    for sFile in listFiles:
        sFilePath = os.path.join(sSrcFolder, sFile)
        with open(sFilePath) as file:
            sContents = file.read()
        if "sUnitAngle" in sContents:
            listWords = sContents.split()
            iIndex = listWords.index("sUnitAngle")
            return listWords[iIndex + 1]
    raise ValueError("sUnitAngle not found in any template file")

def fnHandleDestinationOverride(sDestFolder: str, bForced: bool) -> None:
    """
    Handle destination folder cleanup/override.
    Target: 15 lines.
    """
    if not os.path.exists(sDestFolder):
        return

    if not bForced:
        sPrompt = f"Destination folder '{sDestFolder}' exists. Override? (y/n): "
        sReply = input(sPrompt).lower().strip()
        if not sReply.startswith('y'):
            sys.exit(0)

    fnCleanupDestination(sDestFolder)

def fnCleanupDestination(sDestFolder: str) -> None:
    """Remove destination folder and related files. Target: 8 lines."""
    import shutil
    shutil.rmtree(sDestFolder)

    # Remove bigplanet/multiplanet checkpoint files
    for sExt in ['.bpl', '_bpl']:
        sFile = f"{sDestFolder}{sExt}"
        if os.path.exists(sFile):
            os.remove(sFile)
        sFile = f".{sDestFolder}{sExt}"
        if os.path.exists(sFile):
            os.remove(sFile)
```

**Estimated lines eliminated:** ~150 lines

#### Week 9: Main Refactor & Constants

`vspace/constants.py` (target: ~50 lines):

```python
"""Constants for vspace."""

# Sampling modes
IMODE_GRID = 0
IMODE_RANDOM = 1

# Distribution type identifiers
SDIST_LINEAR = 'n'
SDIST_LOG = 'l'
SDIST_UNIFORM = 'u'
SDIST_LOG_UNIFORM = 't'
SDIST_GAUSSIAN = 'g'
SDIST_LOG_NORMAL = 'G'
SDIST_SINE = 's'
SDIST_COSINE = 'c'
SDIST_PREDEFINED = 'p'

# Input file keywords
TUPLE_SRCFOLDER_KEYS = ('sSrcFolder', 'srcfolder')
TUPLE_DESTFOLDER_KEYS = ('sDestFolder', 'destfolder')
TUPLE_TRIALNAME_KEYS = ('sTrialName', 'trialname')
TUPLE_MODE_KEYS = ('sSampleMode', 'samplemode')
TUPLE_SEED_KEYS = ('iSeed', 'seed')
TUPLE_RANDSIZE_KEYS = ('iNumTrials', 'randsize')
TUPLE_FILE_KEYS = ('sBodyFile', 'sPrimaryFile', 'file')
TUPLE_ANGLEUNIT_KEYS = ('sUnitAngle',)

# Angle units
SANGLE_DEGREES = 'degrees'
SANGLE_RADIANS = 'radians'
```

`vspace/vspace.py` (target: ~80 lines total):

```python
"""VSPACE: Parameter sweep generator for VPLanet."""

from __future__ import print_function
import argparse
import os
import sys

from .parser import fParseConfigFile
from .validators import fnValidateConfig
from .samplers import fnPopulateParameterArrays
from .fileWriter import fnGenerateAllTrials
from .utils import fnHandleDestinationOverride

def fnMain():
    """
    Main entry point for vspace command.
    Target: 15 lines.
    """
    args = fParseArguments()
    config = fParseConfigFile(args.InputFile)
    fnValidateConfig(config)
    fnHandleDestinationOverride(config.sDestFolder, args.force)
    os.makedirs(config.sDestFolder, exist_ok=True)
    fnPopulateParameterArrays(config)
    fnGenerateAllTrials(config)

def fParseArguments():
    """
    Parse command-line arguments.
    Target: 10 lines.
    """
    parser = argparse.ArgumentParser(
        description="Create VPLanet parameter sweep"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force override of destination folder"
    )
    parser.add_argument(
        "InputFile",
        type=str,
        help="Name of the vspace input file"
    )
    return parser.parse_args()

if __name__ == "__main__":
    fnMain()
```

**Phase 2 Complete When:**
- ✅ No function >20 lines
- ✅ All Phase 1 tests passing
- ✅ No code duplication >10 lines
- ✅ main() <20 lines
- ✅ 7 new modules created
- ✅ All functions have docstrings

---

### Phase 3: Style Compliance & Cleanup (Weeks 10-11, MEDIUM PRIORITY)

#### Week 10: Hungarian Notation Application

**Systematic renaming across all modules:**

Create `scripts/applyHungarianNotation.py` to automate:
- Variable renames (track in spreadsheet)
- Function renames (verify with grep)
- Update all tests
- Run full test suite after each module

**Example renames:**
```python
# Before
def parseInput(infile="input"):
    destfolder = "."
    src = "."
    trialname = "test"
    infiles = []

# After
def ftParseInput(sInputFile="input"):
    sDestFolder = "."
    sSrcFolder = "."
    sTrialName = "test"
    listInputFiles = []
```

**Verification:**
- Run pytest after each file rename
- Use IDE refactoring tools (PyCharm, VSCode)
- Ensure no test breakage

#### Week 11: Code Cleanup

**Remove dead code:**
- ❌ Delete `if False:` block (lines 1186-1214)
- ❌ Remove commented code (lines 430-438, 506-514)
- ❌ Remove `import pdb; pdb.set_trace()` (line 1022-1024)
- ❌ Clean up "Megan's Addition" comments

**Error handling standardization:**

Create `vspace/exceptions.py`:
```python
"""Custom exceptions for vspace."""

class VspaceError(Exception):
    """Base exception for vspace."""
    pass

class VspaceConfigError(VspaceError):
    """Invalid configuration."""
    pass

class VspaceValidationError(VspaceError):
    """Validation failed."""
    pass

class VspaceFileError(VspaceError):
    """File operation failed."""
    pass
```

Replace all `IOError` with specific exceptions:
```python
# Before
raise IOError("Source folder does not exist")

# After
raise VspaceFileError(
    f"Source folder '{sSrcFolder}' does not exist. "
    f"Please verify the srcfolder path in your input file."
)
```

**Documentation:**
- Add Google-style docstrings to all functions
- Update module docstrings
- Ensure self-documenting code reduces comment needs

**Formatting:**
- Run `black vspace/ tests/`
- Run `isort vspace/ tests/`
- Update `.pre-commit-config.yaml`

**Phase 3 Complete When:**
- ✅ 100% Hungarian notation compliance
- ✅ Zero dead code in production
- ✅ All exceptions are custom types
- ✅ Black and isort pass
- ✅ All functions have docstrings

---

### Phase 4: Enhanced Testing & Edge Cases (Weeks 12-13, MEDIUM PRIORITY)

#### Week 12: Performance & Integration Tests

`tests/Performance/`:

```python
def test_large_grid_sweep():
    """10,000 trial grid sweep, verify execution time <60s."""
    # 10x10x10x10 grid

def test_large_random_sweep():
    """100,000 random trials, verify execution time <90s."""

def test_memory_usage():
    """Profile memory for large sweeps, verify <1GB."""
```

`tests/Integration/`:

```python
def test_realistic_habitability_sweep():
    """Simulate real research workflow."""
    # earth.in: dSemi [0.8, 1.2, u], dEcc [0, 0.2, u]
    # sun.in: dMass [0.9, 1.1, g]
    # Validate all outputs, histograms, list files

def test_multiplanet_integration():
    """Verify output compatible with multiplanet."""
    # Check vpl.in in each directory
    # Verify grid_list.dat format
```

#### Week 13: Regression & Compatibility Tests

`tests/Regression/`:

```python
def test_output_identical_to_v1_0():
    """Ensure refactored code produces identical output."""
    # Capture output from pre-refactor version
    # Run same inputs through refactored version
    # Compare bit-for-bit (except random with different seed handling)

def test_backward_compatible_inputs():
    """Old vspace.in files still work."""
    # Test with vspace.in files from 2020-2024
```

**Phase 4 Complete When:**
- ✅ Performance benchmarks documented
- ✅ Integration tests pass
- ✅ Regression tests prove equivalence
- ✅ Backward compatibility verified

---

### Phase 5: Hyak Module ~~(Weeks 14-15, LOW PRIORITY)~~ **COMPLETED - DEPRECATED** ✅

**Status: DEPRECATED as of 2025-12-29**

After comprehensive analysis, the Hyak PBS/Torque scheduler integration has been deprecated for the following reasons:

1. **Superseded by multiplanet**: The multiplanet tool provides superior parallel execution with checkpoint/resume functionality that works on any system without scheduler dependencies.

2. **Obsolete technology**: PBS/Torque is legacy; modern HPC uses Slurm. Even UW's Hyak cluster migrated to Slurm in 2020.

3. **Already disabled**: The code was wrapped in `if False:` block (vspace.py:1186-1214), indicating it was not actively used.

4. **Hardcoded for single user**: Paths like `/gscratch/stf/dflemin3/` and email `dflemin3@uw.edu` indicate this was a personal tool never generalized.

**Actions taken:**
- ✅ Deleted `vspace/hyak.py` and `vspace/vspace_hyak.py`
- ✅ Removed `vspace_hyak` import from `vspace/vspace.py`
- ✅ Removed dead code block (lines 1186-1214) from `vspace/vspace.py`
- ✅ Documented deprecation in CLAUDE.md
- ✅ Added deprecation notice to README.md

**Recommendation for users needing HPC integration:**
- Use multiplanet in interactive sessions on clusters
- For true batch scheduling, consider adding Slurm job array support to multiplanet in the future

---

### Phase 6: Documentation & Release (Weeks 16-17, HIGH PRIORITY)

#### Week 16: API Documentation

**Sphinx documentation updates:**

`docs/api/`:
- `parser.rst` - Document all parser functions
- `samplers.rst` - Document all distribution samplers
- `fileWriter.rst` - Document file generation
- `validators.rst` - Document validation functions
- `dataStructures.rst` - Document VspaceConfig, ParameterSpec

`docs/architecture.md`:
```markdown
# VSPACE Architecture

## Design Principles
- Functions <20 lines
- Single responsibility
- Hungarian notation
- Comprehensive testing

## Module Structure
[Diagram showing module relationships]

## Data Flow
[Diagram: Input file → Parser → Validator → Sampler → FileWriter]

## Adding New Distribution Types
[Guide for developers]
```

**Docstring completion:**
- Ensure all public functions have complete docstrings
- Include parameters, returns, raises, examples
- Use Google style consistently

#### Week 17: User Documentation & Release

**Update user docs:**

`docs/install.rst`:
- Update Python version requirements (3.9-3.14)
- Update dependency list
- Add troubleshooting section

`docs/help.rst`:
- Update command-line interface
- Add examples for all distribution types
- Include error message reference

`docs/sampling.rst`:
- Document all distribution types with examples
- Add statistical properties tables
- Include visualization of distributions

`docs/changelog.md`:
```markdown
# Changelog

## v2.0.0 (2025)

### Breaking Changes
- Python 3.6-3.8 support dropped (now 3.9-3.14)
- Internal API completely refactored (input file format unchanged)

### New Features
- Comprehensive test suite (90% coverage)
- Improved error messages
- Performance optimizations

### Bug Fixes
- Fixed negative sigma validation in Gaussian distributions
- [List other fixes]

### Internal Changes
- Refactored into modular architecture
- Applied Hungarian notation throughout
- All functions <20 lines
```

**GitHub updates:**

`.github/workflows/tests.yml`:
```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12', '3.13', '3.14']
```

`README.md`:
- Update badges (test count, coverage percentage)
- Add architecture overview
- Update installation instructions
- Add "What's New in v2.0" section

**Migration guide:**

`docs/migration_v1_to_v2.md`:
```markdown
# Migration Guide: v1.x to v2.0

## For Users
No changes needed! Input file format is unchanged.

## For Developers
[Document API changes if anyone imports vspace as library]
```

**Release preparation:**
- Update version in `vspace_version.py`
- Create release notes
- Tag commit: `git tag v2.0.0`

**Phase 6 Complete When:**
- ✅ All modules documented
- ✅ User documentation updated
- ✅ Changelog complete
- ✅ Migration guide written
- ✅ GitHub Actions passing on all versions
- ✅ README updated
- ✅ Ready for release

---

## Success Metrics

### Overall Project Success

**Code Quality:**
- ✅ Zero functions >20 lines
- ✅ Zero code duplication >10 lines
- ✅ 100% Hungarian notation compliance
- ✅ Zero style guide violations

**Testing:**
- ✅ ≥30 tests (vs 5 current)
- ✅ ≥90% code coverage (vs ~40% current)
- ✅ All distribution types tested
- ✅ All error paths tested
- ✅ Performance benchmarks established

**Documentation:**
- ✅ All public functions documented
- ✅ Architecture guide complete
- ✅ User documentation updated
- ✅ Developer guide written

**Compatibility:**
- ✅ Python 3.9-3.14 supported
- ✅ macOS and Linux tested
- ✅ Backward compatible input files
- ✅ Output format unchanged (except bug fixes)

**Maintainability:**
- ✅ New contributor can understand codebase in <2 hours
- ✅ Adding new distribution type takes <1 hour
- ✅ All tests run in <60 seconds

---

## Risk Mitigation

### Potential Risks & Mitigations

1. **Risk:** Refactoring breaks existing functionality
   - **Mitigation:** Comprehensive tests before refactoring, regression tests with captured outputs

2. **Risk:** Performance degrades with modular structure
   - **Mitigation:** Performance benchmarks, profiling, optimization if needed

3. **Risk:** Tests take too long to run
   - **Mitigation:** Use pytest-xdist for parallel testing, optimize test fixtures

4. **Risk:** Hungarian notation makes code less readable
   - **Mitigation:** Consistent application, clear documentation, IDE autocomplete

5. **Risk:** Backward compatibility issues
   - **Mitigation:** Comprehensive regression tests, migration guide, versioning

6. **Risk:** Timeline slippage
   - **Mitigation:** Weekly checkpoints, adjust scope if needed, prioritize critical items

---

## Development Workflow

### Branch Strategy
```
main (production-ready)
└── refactor/vspace-v2 (development branch)
    ├── feature/phase1-tests
    ├── feature/phase2-refactor
    ├── feature/phase3-style
    └── feature/phase4-enhanced-tests
```

### Commit Strategy
- Small, focused commits
- Each commit passes all tests
- Descriptive commit messages following conventional commits:
  ```
  test: add Gaussian distribution sampling tests
  refactor: extract sampling logic into samplers.py
  style: apply Hungarian notation to parser module
  docs: update API documentation for samplers
  ```

### Review Process
1. Self-review before committing
2. Run full test suite
3. Check coverage report
4. Run black and isort
5. Update documentation if needed
6. Commit with descriptive message

### Testing Discipline
- **Red-Green-Refactor:** Write test (red) → Make it pass (green) → Refactor (green)
- Run tests after every function extraction
- Never commit broken tests
- Aim for <1% flaky tests

---

## Tools & Infrastructure

### Development Tools
- **Python:** 3.9-3.14
- **Testing:** pytest, pytest-cov, pytest-parallel
- **Formatting:** black, isort
- **Linting:** flake8 (configured for style guide)
- **Type Checking:** mypy (optional, for type hints)
- **Documentation:** Sphinx, sphinx_rtd_theme
- **Version Control:** git, GitHub

### IDE Configuration
- **VSCode:** Configure for black, isort, pytest
- **PyCharm:** Enable Hungarian notation spell checking

### CI/CD
- **GitHub Actions:** Run tests on all Python versions, both platforms
- **Coverage:** Upload to Codecov
- **Pre-commit hooks:** Enforce formatting, run fast tests

---

## Open Questions

1. **Python 3.6-3.8 Support:** Drop support for EOL versions?
   - **Recommendation:** Drop 3.6-3.8, support 3.9-3.14

2. **Hyak Module:** Still in use?
   - **Action Required:** Consult with users

3. **Performance:** Acceptable trade-off for clarity?
   - **Approach:** Benchmark first, optimize only if needed

4. **Backward Compatibility:** Guarantee exact output?
   - **Recommendation:** Allow minor improvements (e.g., better error messages)

5. **Type Hints:** Add throughout codebase?
   - **Recommendation:** Add to new code, optional for refactored code

---

## Appendix: Current vs. Target Architecture

### Current Architecture (1 module, 1,615 lines)
```
vspace/
└── vspace.py (1,218 lines)
    └── main() (1,182 lines)
        ├── Parse input file (250 lines)
        ├── Generate parameter arrays (350 lines)
        ├── Write grid trials (161 lines)
        ├── Write random trials (158 lines)
        └── Generate histograms (30 lines)
```

### Target Architecture (7 modules, ~800-1000 lines)
```
vspace/
├── vspace.py (~80 lines)
│   └── fnMain() (~15 lines)
├── constants.py (~50 lines)
├── exceptions.py (~20 lines)
├── dataStructures.py (~60 lines)
│   ├── VspaceConfig
│   └── ParameterSpec
├── parser.py (~150 lines)
│   ├── fParseConfigFile()
│   ├── fnParseGlobalSettings()
│   ├── fnParseFileList()
│   └── fnParseParameters()
├── validators.py (~80 lines)
│   ├── fnValidateConfig()
│   ├── fnValidateSourceFolder()
│   └── fnValidateParameters()
├── samplers.py (~180 lines)
│   ├── fdaGenerateLinearGrid()
│   ├── fdaGenerateLogGrid()
│   ├── fdaSampleUniform()
│   ├── fdaSampleGaussian()
│   └── [10 more samplers]
├── fileWriter.py (~200 lines)
│   ├── fnGenerateAllTrials()
│   ├── fnGenerateGridTrials()
│   ├── fnGenerateRandomTrials()
│   ├── fnWriteTrialFiles()
│   └── [10 more writers]
└── utils.py (~60 lines)
    ├── fsSearchAngleUnit()
    ├── fnHandleDestinationOverride()
    └── fnCleanupDestination()
```

**Benefits:**
- Each module has clear responsibility
- Functions are testable in isolation
- Easy to add new distribution types
- New contributors can understand quickly
- Easier to maintain and debug

---

## Next Steps (Immediate Action Items)

### Week 1 Priority Tasks
1. **Set up test infrastructure** (Day 1-2)
   - Create `tests/RandomDistributions/` directory
   - Create `tests/test_utils.py` with shared utilities
   - Set up fixtures directory structure

2. **Implement critical tests** (Day 3-5)
   - `test_gaussian_negative_sigma.py` ← **HIGHEST PRIORITY** (validates sigmaerror branch)
   - `test_uniform.py` (simplest distribution)
   - `test_seed_reproducibility.py` (critical for science)

3. **Begin systematic testing** (Week 1 ongoing)
   - `test_loguniform.py`
   - `test_gaussian_basic.py`
   - Continue with Week 1 test plan

### Success Checkpoint (End of Week 1)
- ✅ 5-8 new tests passing
- ✅ sigmaerror branch validated
- ✅ Test infrastructure proven

### Adjustment Strategy
- If tests reveal bugs, fix before proceeding
- If timeline slips, prioritize Phase 1 completion
- Reassess scope after Phase 1 complete

---

**Document Version:** 2.0
**Created:** 2025-12-28
**Next Review:** After Phase 1 completion or major changes
**Owner:** Development team

---

## References

- **Parent CLAUDE.md:** `/Users/rory/.claude/CLAUDE.md` - Project-wide coding standards
- **VPLanet:** https://github.com/VirtualPlanetaryLaboratory/vplanet
- **MultiPlanet:** https://github.com/VirtualPlanetaryLaboratory/multi-planet
- **BigPlanet:** https://github.com/VirtualPlanetaryLaboratory/bigplanet
- **VSPACE Docs:** https://VirtualPlanetaryLaboratory.github.io/vspace/
