
<p align="center">
  <img width = "250" src="docs/VPLanetLogo.png?raw=true"/>
</p>

<h1 align="center">Vspace: Parameter Sweeps with VPLanet</h1>

<p align="center">
  <a href="https://VirtualPlanetaryLaboratory.github.io/vspace/"><img src="https://img.shields.io/badge/read-the_docs-blue.svg?style=flat"></a>
   <img src="https://img.shields.io/badge/Python-3.6+-orange.svg"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-purple.svg"/></a>
  <a href="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml">
  <img src="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml/badge.svg"/>
  </a>
</p>


### VSPACE
``VSPACE`` is a tool to build input files for a parameter sweep with ``VPLanet``.

### Overview
With ``VSPACE`` you can quickly and easily build input files with specific
parameters with a specific type of distribution. In **Grid Mode** you can build
input files in which the initial conditions have regular spacings within specified
limits and with either linear or logarithmic spacings. In **Random Mode** the
distributions are random, but can be **uniform, Gaussian** or uniform in **sine**
or **cosine**. Non-uniform distributions can be easily truncated, if necessary.
Histograms of the initial conditions will also be built. After generating the
trials, use the [multi-planet package](https://github.com/VirtualPlanetaryLaboratory/multi-planet) to run.
