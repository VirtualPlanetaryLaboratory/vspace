from __future__ import print_function
from . import vspace_hyak  #relative import does not seem to work here. can't figure out why
# import vspace_hyak
import os
import sys
import numpy as np
import re
import itertools as it
import matplotlib.pyplot as plt
import subprocess as sub
import argparse


def SearchAngleUnit(src, flist):
    """
    Searches *.in files in 'flist' for angle unit in src directory
    """
    for fcurr in flist:
        fread = open(src + "/" + fcurr).read()
        if "sUnitAngle" in fread:
            angUnit = fread.split()[
                np.where(np.asarray(fread.split()) == "sUnitAngle")[0][0] + 1
            ]

    return angUnit

def main():
    parser = argparse.ArgumentParser(description="Create Vplanet parameter sweep")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="forces override of vspace file creation"
    )
    parser.add_argument("InputFile", type=str, help="Name of the vspace input file")
    args = parser.parse_args()
    inputf = args.InputFile
    forced = args.force

    try:
        f = open(inputf, "r")
    except IOError:
        print("%s is not a valid file name. Please reenter." % inputf)


    lines = f.readlines()
    f.close()

    src = None
    dest = None
    trial = "default"
    fnum = 0  # number of files to be copied/edited
    flist = []  # list of files
    fline = []  # list of line numbers associated with each file
    iter_var = []  # list that will contain all iteration variables.
    iter_file = []  # which file each variable belongs to
    iter_name = []  # the name of each variable
    prefix = []
    numtry = 1  # number of trials to be generated
    numvars = 0  # number of iter_vars
    angUnit = 0  # angle unit used for sine and cosine sampling
    mode = (
        0  # sampling mode (0 = grid, 1 = random (also need to set randsize for random))
    )
    randsize = 0  # size of random sample

    #- first pass through input file -------------------------------------------
    #- get basic set up parameters ---------------------------------------------
    for i in range(len(lines)):
        if lines[i].split() == []:
            pass  # nothing on this line
        elif lines[i].split()[0] == "srcfolder":
            #read the folder containing template vplanet *.in files
            src = lines[i].split()[1]
            if "~" in src:  #you can specify a path relative to home directory
                src = os.path.expanduser(src)

        elif lines[i].split()[0] == "destfolder":
            #read the destination folder for resulting input files
            dest = lines[i].split()[1]
            if "~" in dest:  #you can specify a path relative to home directory
                dest = os.path.expanduser(dest)
            if os.path.isdir(dest) == True and forced == True:
                #destination folder exists but you want to overwrite it
                sub.run(["rm", "-rf", dest])
                if os.path.isfile(dest + ".bpl") == True:
                    sub.run(["rm", dest + ".bpl"])
                if os.path.isfile("." + dest + "_bpl") == True:
                    sub.run(["rm", "." + dest + "_bpl"])
                if os.path.isfile("." + dest) == True:
                    sub.run(["rm", "." + dest])
            if os.path.isdir(dest) == True:
                #destination folder exists, ask if user wants to overwrite
                reply = None
                question = (
                    "Destination Folder "
                    + dest
                    + " already exists. Would you like to override it? \nWARNING: This will delete "
                    + dest
                    + ", as well as any checkpoint files and HDF5 files if applicable."
                )
                while reply not in ("y", "n"):
                    reply = str(input(question + " (y/n): ")).lower().strip()
                    if reply[:1] == "y":
                        sub.run(["rm", "-rf", dest])
                        if os.path.isfile(dest + ".bpl") == True:
                            sub.run(["rm", dest + ".bpl"])
                        if os.path.isfile("." + dest + "_bpl") == True:
                            sub.run(["rm", "." + dest + "_bpl"])
                        if os.path.isfile("." + dest) == True:
                            sub.run(["rm", "." + dest])
                    if reply[:1] == "n":
                        exit()

        elif lines[i].split()[0] == "trialname":
            #read in descriptive name for trials within destination folder
            trial = lines[i].split()[1]
        elif lines[i].split()[0] == "samplemode":
            #read in sampling mode choice
            modename = lines[i].split()[1]
            if modename.startswith("g") or modename.startswith("G"):
                #sample on a grid
                mode = 0
            elif modename.startswith("r") or modename.startswith("R"):
                #sample randomly (monte carlo)
                mode = 1
            else:
                raise IOError("samplemode must be grid or random")
        elif lines[i].split()[0] == "seed":
            #for random sampling
            #read in RNG seed for better replicability
            if np.float(lines[i].split()[1]).is_integer():
                np.random.seed(np.int(lines[i].split()[1]))
            else:
                raise IOError("Attempt to pass non-integer value to seed")
        elif lines[i].split()[0] == "file":
            #read in name of template *.in file to copy and add to new sims
            flist.append(lines[i].split()[1])
            fline.append(i)
        elif lines[i].split()[0] == "sUnitAngle":
            #read in user specified angle unit
            angUnit = lines[i].split()[1]
        elif lines[i].split()[0] == "randsize":
            #read in number of random simulations to generate
            if np.float(lines[i].split()[1]).is_integer():
                randsize = np.int(lines[i].split()[1])
            else:
                raise IOError("Attempt to pass non-integer value to randsize")

    #^ end first pass through input file ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    #- second pass through input file ------------------------------------------
    #- identify and check syntax of lines demarking iterations -----------------
    #- build arrays of variables if all input is valid -------------------------
    for i in range(len(lines)):
        if lines[i].split() == []:
            pass  # nothing on this line
        elif lines[i].split()[0] == "file":
            #count the number of .in files we want to copy and add to simulations
            fnum += 1

        if re.search("\[", lines[i]) != None:
            #check if line is a parameter to be varied
            #(i.e., containing bracket [] syntax)
            spl = re.split("[\[\]]", lines[i])
            name = lines[i].split()[0]    #get name of parameter to be varied
            values = spl[1].split(",")    #record values inside brackets
            if len(spl) == 3:
                #line contains correct syntax: name [values] identifier
                prefix.append(spl[2].strip())
            else:
                #line does not contain correct syntax (identifying prefix is missing)
                raise IOError(
                    "Please provide a short prefix identifying each parameter to be iterated (to be used in directory names): <option> [<range>] <prefix>. Prefix is missing for '%s' for '%s'"
                    % (name, flist[fnum - 1])
                )
            if mode == 0:
                #sampling in grid mode
                if len(values) != 3:
                    #exactly three values are required inside brackets in grid mode
                    raise IOError(
                        "Attempt to iterate over '%s' for '%s', but incorrect number of values provided. Syntax should be [<low>, <high>, <spacing>], [<low>, <high>, n<number of points>], or [<low>, <high>, l<number of points>] (log spacing) "
                        % (name, flist[fnum - 1])
                    )

            for j in range(len(values)):
                values[j] = values[j].strip()  # remove any leading white spaces

            if mode == 1:
                #sampling in random mode (monte carlo)
                if len(values) != 3:
                    #if 3 values, we are good. if not, check a few options
                    if values[2][0] == "g":
                        # gaussian sampling for this parameter
                        # permits specification of min and max values
                        if len(values) >= 4 and len(values) < 6:
                            #check if 4th value contains min or max
                            if values[3][:3] == "min":
                                min_cutoff = np.float(values[3][3:])
                            elif values[3][:3] == "max":
                                max_cutoff = np.float(values[3][3:])
                            else:
                                raise IOError(
                                    "Incorrect syntax in Gaussian/normal distribution cutoff for '%s' for '%s'. Correct syntax is [<center>, <width>, g, min<value>], [<center>, <width>, g, max<value>],[<center>, <width>, g, min<value>, max<value>], or [<center>, <width>, g, max<value>, min<value>]"
                                    % (name, flist[fnum - 1])
                                )
                        if len(values) == 5:
                            #check if 5th value contains min or max (if it exists)
                            if values[4][:3] == "min":
                                min_cutoff = np.float(values[4][3:])
                            elif values[4][:3] == "max":
                                max_cutoff = np.float(values[4][3:])
                            else:
                                raise IOError(
                                    "Incorrect syntax in Gaussian/normal distribution cutoff for '%s' for '%s'. Correct syntax is [<center>,<width>,g,min<value>], [<center>,<width>,g,max<value>],[<center>,<width>,g,min<value>,max<value>], or [<center>,<width>,g,max<value>,min<value>]"
                                    % (name, flist[fnum - 1])
                                )
                        if len(values) >= 6:
                            #too many values inside bracket notation
                            raise IOError(
                                "Incorrect syntax in Gaussian/normal distribution cutoff for '%s' for '%s'. Correct syntax is [<center>,<width>,g,min<value>], [<center>,<width>,g,max<value>],[<center>,<width>,g,min<value>,max<value>], or [<center>,<width>,g,max<value>,min<value>]"
                                % (name, flist[fnum - 1])
                            )
                    else:
                        #extra values only allowed in gaussian mode
                        raise IOError(
                            "Attempt to draw from uniform distributions of '%s' for '%s', but incorrect number of values provided. Syntax should be [<low>,<high>,<type of distribution>], where valid types of distributions are u (uniform), s (uniform in sine), or c (uniform in cosine)."
                            % (name, flist[fnum - 1])
                        )

            # user set linear spacing of data
            if values[2][0] == "n":
                if mode == 0:
                    values[2] = values[2][1:]  #remove leading 'n'
                    if np.float(values[2]).is_integer():
                        #if number for linear spacing is an integer, we are good
                        #construct this parameter's grid
                        array = np.linspace(
                            np.float(values[0]), np.float(values[1]), int(values[2])
                        )
                    else:
                        #number for linear spacing was not an integer. exit.
                        raise IOError(
                            "Attempt to iterate over '%s' for '%s', but number of points provided not an integer value"
                            % (name, flist[fnum - 1])
                        )
                else:
                    #tried to set linear spacing in random mode, exit
                    raise IOError(
                        "Attempt to iterate over grid in random mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )


            # user set log spacing of data
            elif values[2][0] == "l":
                if mode == 0:
                    values[2] = values[2][1:]  #remove leading 'l'
                    if np.float(values[0]) < 0:
                        #user has set a negative value for endpoints
                        #signs on left and right ends must agree! (might want to change for some parameters)
                        if np.float(values[2]).is_integer():
                            #check if log spacing has a integer number, we are ok
                            #construct this parameter's grid
                            array = -np.logspace(
                                np.log10(-np.float(values[0])),
                                np.log10(-np.float(values[1])),
                                int(values[2]),
                            )
                        else:
                            #not an integer number of grid points, exit
                            raise IOError(
                                "Attempt to iterate over '%s' for '%s', but number of points provided not an integer value"
                                % (name, flist[fnum - 1])
                            )
                    else:
                        #left edge is not negative
                        if np.float(values[2]).is_integer():
                            #check if log spacing has a integer number, we are ok
                            #construct this parameter's grid
                            array = np.logspace(
                                np.log10(np.float(values[0])),
                                np.log10(np.float(values[1])),
                                int(values[2]),
                            )
                        else:
                            #not an integer number of grid points, exit
                            raise IOError(
                                "Attempt to iterate over '%s' for '%s', but number of points provided not an integer value"
                                % (name, flist[fnum - 1])
                            )
                else:
                    #tried to set log spacing in random mode, exit
                    raise IOError(
                        "Attempt to iterate over grid in random mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            # user wants to randomly sample a normal/gaussian distribution
            elif values[2][0] == "g":
                if mode == 1:
                    #check if user set random mode
                    #if yes, construct array of random samples
                    array = np.random.normal(
                        loc=np.float(values[0]),
                        scale=np.float(values[1]),
                        size=np.int(randsize),
                    )
                    if "min_cutoff" in vars() and "max_cutoff" not in vars():
                        #user has set a min value for this parameter
                        #resample any values below until all are > min_cutoff
                        for ll in np.arange(len(array)):
                            while array[ll] < min_cutoff:
                                array[ll] = np.random.normal(
                                    loc=np.float(values[0]),
                                    scale=np.float(values[1]),
                                    size=1,
                                )
                        del min_cutoff   #clean up so next parameter doesn't have spurious min_cutoff
                    elif "min_cutoff" not in vars() and "max_cutoff" in vars():
                        #user has set a max value for this parameter
                        #resample any values above until all are < max_cutoff
                        for ll in np.arange(len(array)):
                            while array[ll] > max_cutoff:
                                array[ll] = np.random.normal(
                                    loc=np.float(values[0]),
                                    scale=np.float(values[1]),
                                    size=1,
                                )
                        del max_cutoff   #clean up so next parameter doesn't have spurious max_cutoff
                    elif "min_cutoff" in vars() and "max_cutoff" in vars():
                        #user has set min and max values for this parameter
                        #resample any values between the two
                        for ll in np.arange(len(array)):
                            while array[ll] < min_cutoff or array[ll] > max_cutoff:
                                array[ll] = np.random.normal(
                                    loc=np.float(values[0]),
                                    scale=np.float(values[1]),
                                    size=1,
                                )
                        del max_cutoff  #clean up so next parameter doesn't have spurious cutoffs
                        del min_cutoff
                    # elif "min_cutoff" not in vars() and "max_cutoff" not in vars():
                    #     #i can't remember why i resample everything here!
                    #     #wtf??? maybe this can be removed??
                    #     for ll in np.arange(len(array)):
                    #         array[ll] = np.random.normal(
                    #             loc=np.float(values[0]),
                    #             scale=np.float(values[1]),
                    #             size=1,
                    #         )
                else:
                    #tried to set gaussian sampling in grid mode, exit
                    raise IOError(
                        "Attempt to draw from a random distribution in grid mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            # user wants to randomly sample a uniform distribution
            elif values[2][0] == "u":
                if mode == 1:
                    #check if in random mode, all ok
                    #construct array of random samples
                    array = np.random.uniform(
                        low=np.float(values[0]),
                        high=np.float(values[1]),
                        size=np.int(randsize),
                    )
                else:
                    #user tried to use random sampling in grid mode
                    raise IOError(
                        "Attempt to draw from a random distribution in grid mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            # user wants to randomly sample a log-uniform distribution
            elif values[2][0] == "t":
                if mode == 1:
                    # check if in random mode, all ok
                    # construct array of randoms amples
                    if np.float(values[0]) < 0:
                        #user has set a negative value for endpoints
                        #signs on left and right ends must agree! (might want to change for some parameters)
                        array = -np.power(10, np.random.uniform(
                            low=np.log10(-np.float(values[0])),
                            high=np.log10(-np.float(values[1])),
                            size=np.int(randsize),
                        ))
                    else:
                        array = np.power(10, np.random.uniform(
                            low=np.log10(np.float(values[0])),
                            high=np.log10(np.float(values[1])),
                            size=np.int(randsize),
                        ))
                else:
                    #user tried to use random sampling in grid mode
                    raise IOError(
                        "Attempt to draw from a random distribution in grid mode for '%s' for '%s'"
                        % (name, flist[fnum-1])
                    )

            # user wants to randomly sample a uniform distribution of the SINE of an angle
            elif values[2][0] == "s":
                if mode == 1:
                    #check if in random mode, all ok
                    if angUnit == 0:
                        #angle unit was not set, search *.in files for it
                        angUnit = SearchAngleUnit(src, flist)
                    if angUnit.startswith("d") or angUnit.startswith("D"):
                        #angle is degrees, need to do conversion in sine function
                        array = (
                            np.arcsin(
                                np.random.uniform(
                                    low=np.sin(np.float(values[0]) * np.pi / 180.0),
                                    high=np.sin(np.float(values[1]) * np.pi / 180.0),
                                    size=np.int(randsize),
                                )
                            )
                            * 180
                            / np.pi   #convert back to degrees
                        )
                    elif angUnit.startswith("r") or angUnit.startswith("R"):
                        #angle is radians, no conversion
                        array = np.arcsin(
                            np.random.uniform(
                                low=np.sin(np.float(values[0])),
                                high=np.sin(np.float(values[1])),
                                size=np.int(randsize),
                            )
                        )
                    else:
                        #unidentifiable angle units, exit
                        raise IOError(
                            "Cannot randomly sample sin(%s): improper angle units set"
                            % name
                        )
                else:
                    #user tried to use random sampling in grid mode
                    raise IOError(
                        "Attempt to draw from a random distribution in grid mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            # user wants to randomly sample a uniform distribution of the COSINE of an angle
            elif values[2][0] == "c":
                if mode == 1:
                    #check if in random mode, all ok
                    if angUnit == 0:
                        #angle unit was not set, search *.in files for it
                        angUnit = SearchAngleUnit(src, flist)
                    if angUnit.startswith("d") or angUnit.startswith("D"):
                        #angle is degrees, need to do conversion in cosine function
                        array = (
                            np.arccos(
                                np.random.uniform(
                                    low=np.cos(np.float(values[0]) * np.pi / 180.0),
                                    high=np.cos(np.float(values[1]) * np.pi / 180.0),
                                    size=np.int(randsize),
                                )
                            )
                            * 180
                            / np.pi   #convert back to degrees
                        )
                    elif angUnit.startswith("r") or angUnit.startswith("R"):
                        #angle is radians, no conversion needed
                        array = np.arccos(
                            np.random.uniform(
                                low=np.cos(np.float(values[0])),
                                high=np.cos(np.float(values[1])),
                                size=np.int(randsize),
                            )
                        )
                    else:
                        #unidentifiable angle units, exit
                        raise IOError(
                            "Cannot randomly sample cos(%s): improper angle units set"
                            % name
                        )
                else:
                    #user tried to use random sampling in grid mode
                    raise IOError(
                        "Attempt to draw from a random distribution in grid mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            # create custom (posterior) distribution here
            #elif values[2][c] == "p":
            #find file or object with body name (from .in file) and parameter name (name)

            # user set the spacing size of data
            else:
                if mode == 0:
                    if (
                        np.float(values[0]) > np.float(values[1])
                        and np.float(values[2]) > 0
                    ):
                        #check if left is bigger than right end and interval is positive
                        #if so, exit
                        raise IOError(
                            "Attempt to iterate over '%s' for '%s', but start value > end value and spacing is positive"
                            % (name, flist[fnum - 1])
                        )
                    else:
                        #left is smaller than right or interval is negative
                        #all ok, create grid for this parameter
                        array = np.arange(
                            np.float(values[0]),
                            np.float(values[1]) + np.float(values[2]),
                            np.float(values[2]),
                        )
                else:
                    #tried to set log spacing in random mode, exit
                    raise IOError(
                        "Attempt to iterate over grid in random mode for '%s' for '%s'"
                        % (name, flist[fnum - 1])
                    )

            #this parameter was varied, add to iterables
            iter_var.append(array)
            iter_file.append(fnum - 1)
            iter_name.append(name)
            numtry *= len(array)   #multiply total number of trials by length of this parameter's grid
            numvars += 1           #add to the count of variable parameters

    fline.append(i + 1)   #store lines in this input file that correspond to each .in file

    #^ end second pass through input file ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


    # additional error handling ************************************************
    # check whether essential items have all been set and are good
    if src is None:
        raise IOError(
            "Name of source folder not provided in file '%s'. Use syntax 'srcfolder <foldername>'"
            % inputf
        )
    if dest is None:
        raise IOError(
            "Name of destination folder not provided in file '%s'. Use syntax 'destfolder <foldername>'"
            % inputf
        )
    if flist == []:
        raise IOError(
            "No files-to-be-copied provided in file '%s'. Use syntax 'file <filename>'"
        )

    if mode == 1:
        if randsize == 0:
            raise IOError("Must set randsize > 0 for random sampling mode")

    if not os.path.exists(src):
        raise IOError("Source folder '%s' does not exist" % src)

    if re.search("\/", dest) is not None:
        #split up destination folder and check for parent
        #this could be improved to check all subdirectories along path
        dest_parent = "/".join(dest.split("/")[0:-1])
        if not os.path.exists(dest_parent):
            raise IOError(
                "Destination's parent folder '%s' does not exist" % dest_parent
            )
    if not os.path.exists(dest):
        os.system("mkdir " + dest)

    # end additional error handling ********************************************


    #___ set up output and write it to new .in files ___________________________
    if numvars == 0:
        #user did not set any variable parameters
        #create one new directory with modified parameters from input file
        for i in range(fnum):
            # read in file to be copied
            try:
                #check src directory for files set in input file
                #open it if it exists
                fIn = open(os.path.join(src, flist[i]), "r")
            except IOError:
                #couldn't find file set by user in input file
                print(
                    "%s is not a valid file name. Please reenter."
                    % (os.path.join(src, flist[i]))
                )

            # find the lines in 'inputf' that correspond to this file
            slines = lines[fline[i] + 1 : fline[i + 1]]  #get relevant slice
            slines = [slines[j] for j in range(len(slines)) if slines[j].split() != []] #cut out empty lines
            sflag = (
                np.zeros(len(slines)) - 1
            )  # this will be for bookkeeping (has option been found in file?)
            spref = [slines[j].split()[0] for j in range(len(slines))]  # option name
            dlines = fIn.readlines()   #read the lines in the .in file
            fIn.close()                #close it

            # create file out (new .in file)
            fOut = open(os.path.join(dest, flist[i]), "w")

            for j in range(len(dlines)):
                #loop over lines of .in file to check for matches with user set parameters
                for k in range(len(spref)):
                    #loop over lines in input file corresponding to this .in file
                    if dlines[j].split() != []: #skip empty lines
                        if dlines[j].split()[0] == spref[k]:
                            #found a match!
                            sflag[
                                k
                            ] = 1  # option in file to be copied matched with option from inputf
                            dlines[j] = slines[k] #set line in new .in file
                            if dlines[j][-1] != "\n" and j < (len(dlines) - 1):
                                dlines[j] = (
                                    dlines[j] + "\n"
                                ) # add a newline, just in case
                        elif dlines[j].split()[0] == "rm":
                            # remove an option by placing a comment!
                            if dlines[j].split()[1] == spref[k]:
                                dlines[j] = "#" + dlines[j]
                                sflag[k] = 1

                fOut.write(dlines[j])  # write to the copied file

            for k in range(len(spref)):
                # check if any options were not already present in the copied file, then write them
                if sflag[k] < 0:
                    fOut.write("\n" + slines[k])

            fOut.close()

    elif numvars >= 1:
        #at least one parameter is being varied
        #loop over all parameters to be varied
        count = 0  # suffix of directory to be generated
        iter_file = np.array(iter_file)  # convert to numpy array for useful methods
        iter_name = np.array(iter_name)
        iterables0 = [x for x in iter_var]  # create list of iterables

        if mode == 0:  #grid mode
            # iterate over all possible combinations of varied parameters
            histf = open(dest + "/grid_list.dat", "w")  #this will store a list of all simulations and varied parameters
            for tup in it.product(*iterables0):
                if count == 0:  #start header for grid_list file
                    header = "trial "

                current_line = ""   #line in grid_list file, without trial name
                destfull = os.path.join(
                    dest, trial
                )  # create directory for this combination
                for ii in range(len(tup)):
                    #first loop over permutations to build up file name
                    n = len(
                        str(len(iter_var[ii]) - 1)
                    )  # compute number of digits to pad directory index
                    index0 = np.where(iter_var[ii] == tup[ii])[0]
                    destfull += prefix[ii] + np.str(index0[0]).zfill(n) #add identifier to directory name
                    if count == 0:
                        #add body name and option to grid_list file header
                        header += flist[iter_file[ii]][:-3] + "/" + iter_name[ii] + " "
                    current_line += prefix[ii] + np.str(index0[0]).zfill(n) #same as dest name, without trial name
                    if ii != len(tup) - 1:
                        #haven't reached the end of the list of parameters
                        #add a spacer into directory names
                        destfull += "_"
                        current_line += "_"

                for ii in range(len(tup)):
                    #loop through permutations again and store in line to be
                    #written to grid_list
                    current_line += " " + "%f" % tup[ii]

                if count == 0:
                    #first time through, write the grid_list header
                    histf.write(header + "\n")
                histf.write(current_line + "\n") #write each grid_list line

                if not os.path.exists(destfull):
                    #create destination folder if it doesn't already exist
                    os.system("mkdir " + destfull)

                for i in range(fnum):
                    # read in file to be copied (and modified if needed)
                    try:
                        fIn = open(os.path.join(src, flist[i]), "r")
                    except IOError:
                        #file does not exist, exit
                        print(
                            "%s is not a valid file name. Please reenter."
                            % (os.path.join(src, flist[i]))
                        )

                    # find the lines in 'inputf' that correspond to this file
                    slines = lines[fline[i] + 1 : fline[i + 1]]  #get relevant slice
                    slines = [
                        slines[j] for j in range(len(slines)) if slines[j].split() != []
                    ]   #cut out empty lines
                    sflag = (
                        np.zeros(len(slines)) - 1
                    )  # this will be for bookkeeping (has option been found in file?)
                    spref = [
                        slines[j].split()[0] for j in range(len(slines))
                    ]  # option name
                    dlines = fIn.readlines()  #read the lines in the .in file
                    fIn.close()               #close it

                    # create file out (new .in file)
                    fOut = open(os.path.join(destfull, flist[i]), "w")

                    for j in range(len(dlines)):
                        #loop over lines of .in file to check for matches with user set parameters
                        for k in range(len(spref)):
                            #loop over lines in input file corresponding to this .in file
                            if dlines[j].split() != []: #skip empty lines
                                if dlines[j].split()[0] == spref[k]:
                                    #found a match!
                                    sflag[
                                        k
                                    ] = 1  # option in file to be copied matched with option from inputf
                                    dlines[j] = slines[k]   #set line in new .in file
                                    for m in range(len(iter_file)):
                                        if (
                                            iter_file[m] == i
                                            and iter_name[m] == dlines[j].split()[0]
                                        ):
                                            #loop through values to be set in this permutation
                                            #if correct file and param name
                                            #then add that value to the line to be written
                                            dlines[j] = (
                                                dlines[j].split()[0] + " " + str(tup[m])
                                            )
                                    if dlines[j][-1] != "\n" and j < (len(dlines) - 1):
                                        dlines[j] = (
                                            dlines[j] + "\n"
                                        )  # add a newline, just in case
                                elif slines[k].split()[0] == "rm":
                                    # remove an option by placing a comment!
                                    if dlines[j].split()[0] == slines[k].split()[1]:
                                        dlines[j] = "#" + dlines[j]
                                        sflag[k] = 1

                        fOut.write(dlines[j])  # write to the copied file

                    for k in range(len(spref)):
                        # check if any were not already present in the copied file, then write them
                        if sflag[k] < 0:
                            if slines[k].split()[0] == "rm":
                                #user tried to delete an option that did not exist
                                raise IOError(
                                    "No option '%s' to be removed in file %s."
                                    % (slines[k].split()[1], flist[i])
                                )
                            else:
                                #create new option for destination file
                                tmp = slines[k]
                                for m in range(len(iter_file)):
                                    if (
                                        iter_file[m] == i
                                        and iter_name[m] == slines[k].split()[0]
                                    ):
                                        #loop through values to be set in this permutation
                                        #if correct file and param name
                                        #then add that value to the line to be written
                                        tmp = slines[k].split()[0] + " " + str(tup[m])
                                if tmp[-1] != "\n":
                                    tmp = tmp + "\n"
                                fOut.write("\n" + tmp)

                fOut.close()   #close new .in file
                count += 1  # move to next combination
            histf.close()  #close grid_list file

        else:
            # random draw, iterate linearly
            n = len(str(randsize - 1))  # number of digits to pad directory index
            histf = open(dest + "/rand_list.dat", "w")  #file with list of varied params
            for count in np.arange(randsize):
                #loop over random trials
                tup = []
                if count == 0:  #start header for rand_list file
                    header = "trial "
                current_line = "rand_" + np.str(count).zfill(n) + " "  #line in rand_list file
                for ii in np.arange(len(iterables0)):
                    #loop over trials, add values of each variable
                    try:
                        tup.append(iterables0[ii][count])
                    except:
                        import pdb; pdb.set_trace()
                    if count == 0:
                        #add body name and option to rand_list file header
                        header += flist[iter_file[ii]][:-3] + "/" + iter_name[ii] + " "
                    current_line += "%f" % iterables0[ii][count] + " " #add values from this trial

                if count == 0:
                    #first time through, write the rand_list header
                    histf.write(header + "\n")
                histf.write(current_line + "\n") #write each rand_list line

                destfull = os.path.join(
                    dest, trial
                )  # create directory for this combination
                destfull += "rand_" + np.str(count).zfill(n)
                if not os.path.exists(destfull):
                    #create destination folder if it doesn't already exist
                    os.system("mkdir " + destfull)

                for i in range(fnum):
                    # read in file to be copied (and modified if needed)
                    try:
                        fIn = open(os.path.join(src, flist[i]), "r")
                    except IOError:
                        #file does not exist, exit
                        print(
                            "%s is not a valid file name. Please reenter."
                            % (os.path.join(src, flist[i]))
                        )

                    # find the lines in 'inputf' that correspond to this file
                    slines = lines[fline[i] + 1 : fline[i + 1]]  #get relevant slice
                    slines = [
                        slines[j] for j in range(len(slines)) if slines[j].split() != []
                    ]  #cut out empty lines
                    sflag = (
                        np.zeros(len(slines)) - 1
                    )  # this will be for bookkeeping (has option been found in file?)
                    spref = [
                        slines[j].split()[0] for j in range(len(slines))
                    ]  # option name
                    dlines = fIn.readlines()   #read the lines in the .in file
                    fIn.close()                #close it

                    # create file out (new .in file)
                    fOut = open(os.path.join(destfull, flist[i]), "w")

                    for j in range(len(dlines)):
                        #loop over lines of .in file to check for matches with user set parameters
                        for k in range(len(spref)):
                            #loop over lines in input file corresponding to this .in file
                            if dlines[j].split() != []: #skip empty lines
                                if dlines[j].split()[0] == spref[k]:
                                    #found a match!
                                    sflag[
                                        k
                                    ] = 1  # option in file to be copied matched with option from inputf
                                    dlines[j] = slines[k]   #set line in new .in file
                                    for m in range(len(iter_file)):
                                        if (
                                            iter_file[m] == i
                                            and iter_name[m] == dlines[j].split()[0]
                                        ):
                                            #loop through values to be set in this permutation
                                            #if correct file and param name
                                            #then add that value to the line to be written
                                            dlines[j] = (
                                                dlines[j].split()[0] + " " + str(tup[m])
                                            )
                                    if dlines[j][-1] != "\n" and j < (len(dlines) - 1):
                                        dlines[j] = (
                                            dlines[j] + "\n"
                                        )  # add a newline, just in case
                                elif slines[k].split()[0] == "rm":
                                    # remove an option by placing a comment!
                                    if dlines[j].split()[0] == slines[k].split()[1]:
                                        dlines[j] = "#" + dlines[j]
                                        sflag[k] = 1

                        fOut.write(dlines[j])  # write to the copied file

                    for k in range(len(spref)):
                        # check if any were not already present in the copied file, then write them
                        # import pdb; pdb.set_trace()
                        if sflag[k] < 0:
                            if slines[k].split()[0] == "rm":
                                raise IOError(
                                    "No option '%s' to be removed in file %s."
                                    % (slines[k].split()[1], flist[i])
                                )
                            else:
                                if slines[k].split()[0] in iter_name:
                                    #parameter is being varied
                                    m = np.where(iter_name == slines[k].split()[0])[0][0]
                                    if iter_file[m] == i:
                                        #check we're in the right file
                                        fOut.write("\n"+slines[k].split()[0]+" "+str(tup[m])+"\n");
                                    else:
                                        #not iterating over variable in this file
                                        fOut.write("\n" + slines[k])
                                else:
                                    #not iterating over this variable
                                    fOut.write("\n" + slines[k])

                fOut.close()  #close new .in file

            histf.close()   #close grid_list file

            for ii in np.arange(len(iterables0)):
                #generate histogram of simulations
                plt.figure(figsize=(8, 8))
                plt.hist(
                    iterables0[ii], histtype="stepfilled", color="0.5", edgecolor="None"
                )
                plt.xlabel(iter_name[ii])
                plt.ylabel("Number of trials")
                plt.savefig(
                    dest
                    + "/hist_"
                    + flist[iter_file[ii]][:-3]
                    + "_"
                    + iter_name[ii]
                    + ".pdf"
                )
                plt.close()

    #___ end set up output and write it to new .in files _______________________

    # Just do this block if you want to
    if False:
        # Now that all the simulation directories have been populated,
        # Make the submission scripts for hyak
        # Parse input file

        # TODO: allow the input file to include flags to set default things for
        # the .pbs script and for whether or not to run this section

        # Parallel or parallel_sql? Always use parallel_sql!
        para = "parallel_sql"

        destfolder, trialname, infiles, src = vspace_hyak.parseInput(infile=inputf)

        # Make command list and .sh files to run the scripts
        vspace_hyak.makeCommandList(simdir=destfolder, infile=inputf, para=para)

        # Make the submission script
        vspace_hyak.makeHyakVPlanetPBS(
            script="run_vplanet.pbs",
            taskargs="vplArgs.txt",
            walltime="00:30:00",
            para=para,
            simdir=destfolder,
            logdir=destfolder,
        )



if __name__ == "__main__":
    main()
