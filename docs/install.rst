Installation Guide
==================

There are two ways to install ``vspace``: 1) in conjunction with 
`VPLanet <https://github.com/VirtualPlanetaryLaboratory/vplanet>`_ and 
its other support scripts, or 2) from source.

To install ``vspace`` and the other ``VPLanet`` packages, use the command:

.. code-block:: bash

    python -m pip install vplanet

To install from source, first close the repo:


.. code-block:: bash

    git clone https://github.com/VirtualPlanetaryLaboratory/vspace.git

and then go into the directory (vspace) and run the setup script:

.. code-block:: bash

    cd vspace
    python setup.py install