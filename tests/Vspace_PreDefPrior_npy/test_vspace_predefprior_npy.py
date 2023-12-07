import pathlib
import subprocess
import sys
import shutil
from astropy.io import ascii 

def test_vspace_predefprior_npy():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    dir = (path / "Npy_PredefPrior_Test")

    # Remove anything from previous tests
    if (dir).exists():
        shutil.rmtree(dir)

    # Run vspace
    subprocess.check_output(["vspace", "vspace_npy.in"], cwd=path)

    # Grab the dat list of randomly selected priors
    priors = ascii.read(str(dir)+'/rand_list.dat')

    # Check the right number of samples were taken
    assert len(priors) == 3, "The number of random samples (randsize) should be 3"

    # Check all the eccentricities were sampled from the first column of the predefined prior data
    ecc_within = [1, 4, 7, 10]
    for x in priors['earth/dEcc']:
        assert x in ecc_within, "One or more eccentricities were not sampled from the first column of the data file"

    # Check all the radii were sampled from the third (last) column of the predefined prior data
    rad_within = [3, 6, 9, 12]
    for x in priors['earth/dRadius']:
        assert x in rad_within, "One or more radii were not sampled from the third (last) column of the data file"

    # Check that the relationship between priors was preserved
    # i.e., the eccentricity & radius of a particular sample are from the same row in the data file
    for i in range(len(priors)):
        if priors['earth/dEcc'][i] == 1:
            assert priors['earth/dRadius'][i] == 3, "Relationship between priors was not preserved"
        elif priors['earth/dEcc'][i] == 4:
            assert priors['earth/dRadius'][i] == 6, "Relationship between priors was not preserved"
        elif priors['earth/dEcc'][i] == 7:
            assert priors['earth/dRadius'][i] == 9, "Relationship between priors was not preserved"
        elif priors['earth/dEcc'][i] == 10:
            assert priors['earth/dRadius'][i] == 12, "Relationship between priors was not preserved"
    

if __name__ == "__main__":
    test_vspace_predefprior_npy()