Input Files
===========

vspace.in
---------

The input file contains a list of template files and all the ``VPLanet`` options to vary.
An example input file, called ``vspace.in``, is included in this directory and its
lines are described below and is based off the 
`IoHeat example <https://virtualplanetarylaboratory.github.io/vplanet/examples/IoHeat.html>`_.

.. code-block:: bash
    :linenos:

    srcfolder .
    destfolder data
    trialname  ioheat_

    file   vpl.in

    file   jupiter.in

    file   io.in
    dEcc  [0.001,0.005,n5] ecc
    dObliquity [0,10,n5] obl

The first line provides ``VSPACE`` with the location of a directory that contains the template
``VPLanet`` input files, such as vpl.in, star.in, etc. The format of these files
is slightly different when used with ``VSPACE`` then when used with a single ``VPlanet`` run (see below).


Line 2 presents the name of the subdirectory that will contain all the initial conditions for 
the parameter sweep. In other words, a new directory called "data" will be created.

Line 3 specifies a prefix for subdirectories in the *destfolder*. If this option is not set, the prefix is
set to "default". With these top-level commands executed, the remaining lines describe how the
individual parameters are to be varied and completes the names of the trial directories. The general 
syntax for these lines are:

.. code-block:: bash

    file <name>
    <option> <sampling rule> <identifier>
    <option> <sampling rule> <identifier>
    ...

where <name> is the name of the input file, <option> is the name of a ``VPLanet``
input option (exact match required), <sampling rule> sets how the values of the option 
are to be sampled (described in more detail below in the `Sampling
Rules <sampling>`_ section), and <identifier> is a string that is appended to the trialname
prefix in the destfolder subdirectories. ``VSPACE`` will vary all parameters listed
after a "file" command until it reaches the next "file" command or the end of the
file. In this case the "n5" rule tells ``VSPACE`` to create 5 evenly space values of dEcc between 0.001
and 0.005.

This example will create subdirectories with names like

.. code-block:: bash

    data/ioheat_ecc0obl0

each with the files jupiter.in, io.in, and vpl.in that would be identical to those files
in the srcfolder, **except** dEcc and dObliquity would have values that follow the
sampling rules. The numbers after each <identifier> uniquely identifies the
subdirectory.

Once the directories have been created, they can all be executed with a single command
using the `multi-planet <https://github.com/VirtualPlanetaryLaboratory/multi-planet>`_ script and
the vspace.in file.

Template Files
--------------

The template files are nearly identical to standard ``VPLanet`` input files except
that they should not include the parameters to be varied. 

You can additionally instruct ``VSPACE`` to remove options from a template file with by including a line in
vspace.in like: 

.. code-block:: bash

    rm <option name>

``VSPACE`` will merely comments out the matching line.