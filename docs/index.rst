VSPACE Documentation
====================
``VSPACE`` is a tool to build input files for a parameter sweep with ``VPLanet``, creating
a set of individual directories that contain ``VPLanet`` input files that are ready to be simulated.

With ``VSPACE`` you can quickly and easily build input files with specific
parameters with a specific type of distribution. In **Grid Mode** you can build
input files in which the initial conditions have regular spacings within specified
limits and with either linear or logarithmic spacings. In **Random Mode** the
distributions are random, but can be **uniform, Gaussian** or uniform in **sine**
or **cosine**. Non-uniform distributions can be easily truncated, if necessary.
Histograms of the initial conditions will also be built. After generating the
trials, use the `multiplanet <https://github.com/VirtualPlanetaryLaboratory/multi-planet>`_ 
script to run.

.. toctree::
   :maxdepth: 1

   install
   help
   sampling
   GitHub <https://github.com/VirtualPlanetaryLaboratory/vspace>

.. note::

    To maximize ``VSPACE``'s power, run ``mulitplanet`` with the ``-bp`` flag to automatically
    build a BigPlanet archive immediately after the simulations finish.  Then create 
    BigPlanet files from the archive as needed, and use ``BigPlanet``'s `scripting functions <https://virtualplanetarylaboratory.github.io/bigplanet/Script.html>`_ to 
    extract vectors and matrices for plotting, statistical analyses, etc.