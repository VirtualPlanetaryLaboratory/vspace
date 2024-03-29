# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:55:46 2016

@author: dflemin3

This script produces an input file to be used with the hyak "parallel" command
or the parallel_sql paradigm.

Note: parallel keeps all the cores of 1 (!) node active with jobs while
parallel_sql is in general better and distributes the jobs to all the
cores on N nodes where the user specifies N

Essentially, this script reads in the "input" file passed as an arg to vspace,
parses it, and makes a file that has all the commands to be ran.  For example,
if vspace makes 100 folders with 100 unique simulations to run, this function
will return a text file with 100 lines corresponding to each simulation run of
the form:

cd /path/to/simulation/directory
vplanet vpl.in

This way, the parallel command will see this and intelligently distribute all
these single jobs to separate cores on a given node keeping all the cores
active to maximize job productivity.

For reference, a typical input file looks like this:

srcfolder  ../../examples/binary_test
destfolder  test
trialname  binary

file    k16b.in
dFreeEcc   [0.0,0.2,0.05] fe
dFreeInc   [0.0, 10.0, 1.0] fi

file   primary.in

file   secondary.in

file   vpl.in
dStopTime  10000

Key:

srcfolder is where the initial set of vplanet input files are
destdir is where the user wants the output (.pbs file, args file)

"""

# Imports
import os
import stat


def parseInput(infile="input"):
    """
    Given the name of an input file and a source directory,
    parse the input file to extract the destination directories
    and other bits on interest.

    """

    # Inits
    destfolder = "."
    src = "."
    trialname = "test"
    infiles = []

    with open(infile) as f:
        lines = f.readlines()

        # Loop over lines, clean them up, find stuff
        for line in lines:
            line = str(line).rstrip("\n")

            if "destfolder" in line:
                destfolder = line.split()[-1]

            if "trialname" in line:
                trialname = line.split()[-1]

            if "file" in line:
                infiles.append(line.split()[-1])

            if "srcfolder" in line:
                src = line.split()[-1]

    return destfolder, trialname, infiles, src


# end function


def makeCommandList(
    simdir=".", outfile="vplArgs.txt", infile="input", para="parallel_sql"
):
    """
    Given the path to a directory containing a bunch of simulation subdirectories
    generated by vspace, produce a text file listing all the source directories
    as run commands of the form:

    run_sim1.sh contains:

    cd /dir/where/simulation/is
    vplanet vpl.in

    since this format plays nice with the parallel command on hyak.

    Parameters
    ----------
    simdir : string
        path to directory where all simulation sub-directories are located
    outfile : string
        name of the output file
    para : str
        which command you intend to use: parallel or parallel_sql

    Returns
    -------
    None
        ...but it produces a file in the destination dir as described above
    """
    count = 0  # Keeps track of how many run sim commands have been written
    destdir = simdir

    # destdir, trialname, infiles, src = parseInput(infile)
    # import pdb; pdb.set_trace()
    # Get list of all directories in simdir via stack overflow black magic
    # This also ignores all non-directories and ., .. which is convienent
    dirs = filter(
        os.path.isdir, [os.path.join(destdir, f) for f in os.listdir(destdir)]
    )

    if para == "parallel" or para == "parallel_sql":
        # Open file that contains all scripts to be ran by parallel
        with open(os.path.join(destdir, outfile), "w") as f:
            # Loop over all simulation directories where line is dir address
            for line in dirs:
                # Write a .sh file that tells parallel what to run
                command = os.path.join(destdir, "sim")
                command = command.rstrip("\\") + str(count) + ".sh"
                # Open new.sh file with bash commands to run vplanet
                with open(command, "w") as g:
                    g.write("#!/bin/bash\n")
                    g.write("cd " + line + "\n")  # Change dir to where sim is
                    g.write("vplanet vpl.in\n")  # Run sim command!
                # Now give that .sh file execute permissions
                st = os.stat(command)
                os.chmod(command, st.st_mode | stat.S_IEXEC)

                # Write .sh file to master file that gets cat'd to parallel
                command = command + "\n"
                f.write(command)

                # Increment count
                count = count + 1
    elif para == "parallel_sql_junk":
        # Parallel and parallel_sql do (at least should do) the same here
        pass
        # Open file that contains all scripts to be ran by parallel-sql
        with open(os.path.join(destdir, outfile), "w") as f:
            # Loop over all simulation directories where line is dir address
            # Write command that looks like this:
            # app -input (input file(s)) -output (output files)
            for line in dirs:
                # Write a sim's run command
                command = os.path.join("vplanet ", line, "vpl.in")
                command += "\n"

                f.write(command)

    else:
        print("Invalid para: %s" % para)
        return None

    return None


# end function


def makeHyakVPlanetPBS(
    script="run_vplanet.pbs",
    taskargs="vplArgs.txt",
    jobName="vpl_suite",
    nodes=1,
    cores=16,
    mem=20,
    walltime="00:30:00",
    simdir="/gscratch/stf/dflemin3/vpl_sims/",
    logdir="/gscratch/stf/dflemin3/vpl_sims/",
    logfile="vpl_sim.log",
    email="dflemin3@uw.edu",
    para="parallel_sql",
):
    """
    Creates a .pbs script used to run hyak via the command
        qsub out_of_this_function.pbs -Hyak -Flags
    This function assumes you have vplanet/vspace properly installed
    such that vplanet is in your path.

    Parameters
    ----------
    script : string
        name of the .pbs script outputted by the function
    taskargs : string
        name of file that has commands to run like ./runsim1.sh
    jobName : string
        name of the job you tell hyak
    nodes : int
        number of nodes to use.  Must be 1
    cores : int
        number of cores per node. Must be 12 or 16
    walltime : string
        format: xx:xx:xx in hr:min:sec.  how long to run the sim suite
    simdir : string
        root dir where all the simulation sub dirs are.  Should also contain
        scripts like the .pbs file and stuff
    logdir : string
        directory where you want your logfile to appear
    logfile : string
        name of logfile to catch stdout/stderr
    email : string
        email address where you want all hyak communication to go
    para : str
        which command you intend to use: parallel or parallel_sql

    Returns
    -------
    None
        ...but it writes a .pbs file as described above
    """

    # Sanity checks to prevent hyak and me from hating user
    if nodes > 1:
        print(
            "ERROR: Nodes MUST be 1 per hyak wiki. Your value: %d.\n" % nodes
        )
        return -1
    if cores != 12 and cores != 16:
        print("ERROR: Must have 12 or 16 cores. Your value: %d.\n" % cores)
        return -1
    if type(walltime) != str:
        print(
            "ERROR: walltime must be a string like xx:xx:xx in hr:min:sec\n."
        )
        return -1
    if type(mem) != int:
        print("ERROR: mem must be an int amount of gb.\n")
        return -1

    # Write the pbs file.  It's a little tedious, but format matters
    with open(os.path.join(simdir, script), "w") as f:

        # Write header block to file
        f.write("#!/bin/bash\n")
        f.write("##\n")
        f.write(
            "## !! _NEVER_ remove # signs from in front of PBS or from the line above !!\n"
        )
        f.write("##\n")
        f.write("## RENAME FOR YOUR JOB\n")
        f.write("#PBS -N " + str(jobName) + "\n")
        f.write("#PBS -M " + str(email) + "\n")
        f.write("\n")

        # Write node/core block
        f.write("## EDIT FOR YOUR JOB\n")
        f.write("## For 16 core nodes.\n")
        f.write("## Nodes should _never_ be > 1.\n")
        word = "#PBS -l nodes=" + str(nodes)
        word = word + ":ppn=" + str(cores) + ","
        word = word + "mem=" + str(mem) + "gb,"
        word = word + "feature=" + str(cores) + "core\n"
        f.write(word)
        f.write("\n")

        # Write walltime block
        f.write("## WALLTIME DEFAULTS TO ONE HOUR. SPECIFY FOR LONGER JOBS\n")
        f.write("## If the job doesn't finish in 10 minutes, cancel it\n")
        word = "#PBS -l walltime=" + str(walltime) + "\n"
        f.write(word)
        f.write("\n")

        # Write stdout/stderr handling block
        f.write("## EDIT FOR YOUR JOB\n")
        f.write(
            "## Put the STDOUT and STDERR from jobs into the below directory\n"
        )
        word = "#PBS -o " + str(logdir) + "\n"
        f.write(word)
        f.write("## Put both the stderr and stdout into a single file\n")
        f.write("#PBS -j oe\n")
        f.write("\n")

        # Write block pertaining to where the job's working directory is
        f.write("## EDIT FOR YOUR JOB\n")
        f.write("## Specify the working directory for this job bundle\n")
        word = "#PBS -d " + str(simdir) + "\n"
        f.write(word)
        f.write("\n")

        if para == "parallel":
            # Set HYAK_SLOTS to number of tasks started
            #  # If you can't run as many tasks as there are cores due to memory constraints
            #  # you can simply set HYAK_SLOTS to a number instead.
            #  # HYAK_SLOTS=4
            #  HYAK_SLOTS=`wc -l < $PBS_NODEFILE`
            f.write("HYAK_SLOTS=`wc -l < $PBS_NODEFILE`\n")

            # Write block to prevent exceeding local ram
            f.write(
                "# Prevent tasks from exceeding the total RAM of the node\n"
            )
            f.write(
                "# Requires HYAK_SLOTS to be set to number of tasks started.\n"
            )
            f.write(
                "NODEMEM=`grep MemTotal /proc/meminfo | awk '{print $2}'`\n"
            )
            f.write("NODEFREE=$((NODEMEM-2097152))\n")
            f.write("MEMPERTASK=$((NODEFREE/HYAK_SLOTS))\n")
            f.write("ulimit -v $MEMPERTASK\n")
            f.write("\n")
        elif para == "parallel_sql":
            f.write(
                "# If you can't run as many tasks as there are cores due to memory constraints\n"
            )
            f.write("# you can simply set HYAK_SLOTS to a number instead.\n")
            f.write("# HYAK_SLOTS=4\n")
            f.write("HYAK_SLOTS=`wc -l < $PBS_NODEFILE`\n")
        else:
            print("Error: Invalid para: %s." % para)
            return None

        if para == "parallel":
            # Finally, write the block that actually runs the jobs in parallel
            f.write(
                "## jobargs is a file with the arguments you want to pass to your application\n"
            )
            f.write("##\n")
            word = "cat " + taskargs + " | parallel -j $HYAK_SLOTS --joblog"
            word = word + " " + logfile + " --resume\n"
            f.write(word)
            f.write("exit 0\n")
        elif para == "parallel_sql":
            # parallel and parallel_sql actually are different here
            # Write the block that actually runs the jobs!
            f.write("module load parallel_sql\n")
            f.write(
                "parallel_sql --sql -a parallel --exit-on-term -j $HYAK_SLOTS\n"
            )
        else:
            print("Error: Invalid para: %s." % para)
            return None

    # end write

    return None


# end function
