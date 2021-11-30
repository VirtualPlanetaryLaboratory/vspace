Sampling Rules
==============

``VSPACE`` has two sampling modes: **grid** and **random**, which are specified with the word
"samplemode" in the input file (vspace.in). For example:

    samplemode random

will allow you to generate trials that are randomly distributed by a "sampling rule". If *samplemode* 
is not set, the default is grid mode.

Grid Mode
---------

``VSPACE`` allows for 3 submodes to generate trials that explore a gridded parameter
space, i.e even spacing. These submodes are **explicit**, **linear**, and
**logarithmic**. Each adheres the following syntax:

    <option> [start, end, spacing] <identifier>

In all modes the "start" and "end" values represent the limits of the parameter
to be surveyed and are inclusive of the end points. <identifier> is the predfix to be 
used in directory names.

Explicit Grids
^^^^^^^^^^^^^^

In this grid submode, the "spacing" value is just a number that represents the
interval in between trials. ``VSPACE`` will create as many trials as necessary
to follow the sampling rules, and will not necessarily include a trial at the
end value. For example, to generate trials that vary ``dSemi`` from 1 to 2
with a spacing of 0.1, the syntax is:

    dSemi  [1, 2, 0.1]  a

Linear Grids
^^^^^^^^^^^^

To sample the grid linearly with a specific number of trials
that are evenly spaced, the spacing argument must star with an "n" followed
by an integer that represents the number of values to generate. For example, the
previous example could be rewritten as

    dSemi  [1, 2, n11]  a

which would generate 11 trials, equally spaced, from 1 to 2, i.e. every 0.1.

Negative values are allowed, but if you are providing the spacing,
rather than using the "n" or "l" option, either provide a negative spacing or
swap the start and end values. For example:

    dRadius  [-1, -2, -0.1]  R

or,

    dRadius  [-2, -1, 0.1]  R

rather than ``dRadius [-1, -2, 0.1]  R``.

.. warning::
    
    ``VSPACE`` will NOT check whether a minus option causes
    ``VPLanet`` to change the units.
    If you use negative values for a parameter that has alternate units for a
    negative option, the outcome will most likely be wrong! You can check the `VPLanet documentation <https://virtualplanetarylaboratory.github.io/vplanet/help.html#input-options>`_
    or by running ``vplanet -h``.

Logarithmic Grids
^^^^^^^^^^^^^^^^^^^
To change the spacing to be logarithmic, use "l" instead of "n":

    dSemi  [1, 1000, l10]  a

which would generate ten trials, logarithmically spaced, from 1 to 1000.

.. warning::

    As described above, you can vary more than one parameter at a time. While this
    can be very useful, **you have the power to generate a large number of files very
    quickly**. Use this feature wisely: test with small numbers first to ensure that files appear
    in the correct locations and that initial conditions are indeed output with
    the desired values (check the histograms).

Random Mode
-----------

The random mode contains four submodes: **uniform**, **Gaussian**, **sine** and
**cosine**. The syntax for generating randomly sampled data is similar to grid
mode, with a few noteable differences. In random mode, one MUST set the variable
``randsize`` to an integer value that is the number of trials:

    randsize <number of trials>

Additionally, it is good practice to seed the random number generator, to allow for
more easily reproducible results. This initialization is accomplished with the
variable ``seed``:

    seed <integer>

With these options set, we can now specify how each parameter is varied.

.. note::

    It is not possible to mix grid and random modes.

Uniform Distributions
^^^^^^^^^^^^^^^^^^^^^

A uniform distribution is sampled like so:

        <option> [<min>, <max>, u] <prefix>

where <min> and <max> are the limits. Since the number of trials is set by the *randsize* option,
we do not need to specify it again here.

Gaussian Distributions
^^^^^^^^^^^^^^^^^^^^^^

For Gaussian/normal distributions, the syntax is:

    <option> [<mean>, <width/stdev>, g] <prefix>

An example would be:

    dEcc  [0.1, 0.01, g]  e

For some parameters, you may want to truncate the distribution at certain values,
for example, dEcc should not be < 0 or > 1. You can provide cutoffs with 4th and/or
5th arguments in the brackets with the keywords "min" or "max":

    dEcc  [0.1, 0.01, g, min0.0, max1.0]  e

You do not need to provide both min and max if you need only one, and their order does
not matter.

Sine and Cosine Distributions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For angles, you may want to sample the sine or cosine of the angle uniformly,
rather than sampling the angle itself uniformly. You can accomplish this
with ``s`` or ``c``, for sine and cosine, respectively:

    <option> [<low angle>, <high angle>, s] <prefix>

    <option> [<low angle>, <high angle>, c] <prefix>

Note that <low angle> and <high angle> should be the min and max values of the **ANGLE**,
not the sine or cosine of the angle. 

.. note:: 
    
    The units of the angle can be either radians or degrees, but
    must be consistent with your template file. 

Histograms
----------

If running in random mode, ``VSPACE`` will automatically generate histograms of the varied parameters.
In the *destfolder* will be PNG files with plots of each parameter's distribution. These plots are not
publication ready, but can be used to verify that the distributions created match your expectations.