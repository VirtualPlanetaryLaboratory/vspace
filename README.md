<p align="center">
  <img width = "250" src="docs/VPLanetLogo.png"/>
</p>

<h1 align="center">VSPACE: Generate Parameter Spaces for VPLanet</h1>

<p align="center">
  <a href="https://VirtualPlanetaryLaboratory.github.io/vspace/"><img src="https://img.shields.io/badge/read-the_docs-blue.svg?style=flat"></a>
  <a href="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/docs.yml">
  <img src="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/docs.yml/badge.svg">   
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-purple.svg"></a>
    <a href="https://VirtualPlanetaryLaboratory.github.io/vplanet/conduct.html"><img src="https://img.shields.io/badge/Code%20of-Conduct-7d93c7.svg"></a>
  <br>
  <img src="https://img.shields.io/badge/Unit%20Tests-48-darkblue.svg"></a>
  <a href="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml">
  <img src="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml/badge.svg">
    <img src="https://img.shields.io/badge/Python-3.9--3.14-orange.svg"></a>
  <a href="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/pip-install.yml">
  <a href="https://codecov.io/github/VirtualPlanetaryLaboratory/vspace">
  <img src="https://codecov.io/github/VirtualPlanetaryLaboratory/vspace/graph/badge.svg?token=6Z8HVQW8N6">
</a>
  <br>
  <img src="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/pip-install.yml/badge.svg">
    <img src="https://img.shields.io/badge/Python-3.9--3.14-orange.svg"></a>
    <img src = "https://img.shields.io/badge/Platforms-Linux_|%20macOS-darkgreen.svg?style=flat">
  </a>
</p>



`VSPACE` is a tool to build input files for parameter sweeps with [`VPLanet`](https://github.com/VirtualPlanetaryLaboratory/vplanet).
With `VSPACE` you can quickly and easily build input files with specific
parameters with different distributions, such as grids, normal distribution, sines and cosines, and even arbitrary distributions. After generating the trials, use the [`MultiPlanet` package](https://github.com/VirtualPlanetaryLaboratory/multi-planet) to run the simulations
on multi-core platforms, and use [`BigPlanet`](https://github.com/VirtualPlanetaryLaboratory/bigplanet) to store and quickly analyze the results. [Read the docs](https://VirtualPlanetaryLaboratory.github.io/vspace/) to learn how to generate VPLanet parameter sweeps.
