<p align="center">
  <img width = "250" src="docs/VPLanetLogo.png?raw=true"/>
</p>

<h1 align="center">VSPACE: Generate Parameter Spaces for VPLanet</h1>

<p align="center">
  <a href="https://VirtualPlanetaryLaboratory.github.io/vspace/"><img src="https://img.shields.io/badge/read-the_docs-blue.svg?style=flat"></a>
   <img src="https://img.shields.io/badge/Python-3.6+-orange.svg"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-purple.svg"/></a>
  <a href="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml">
  <img src="https://github.com/VirtualPlanetaryLaboratory/vspace/actions/workflows/tests.yml/badge.svg"/>
  </a>
</p>

`VSPACE` is a tool to build input files for parameter sweeps with [`VPLanet`](https://github.com/VirtualPlanetaryLaboratory/vplanet).
With `VSPACE` you can quickly and easily build input files with specific
parameters with different distributions, such as grids, normal distribution, even sines and cosines. After generating the trials, use the [`MultiPlanet` package](https://github.com/VirtualPlanetaryLaboratory/multi-planet) to run the simulations
on multi-core platforms, and use [`BigPlanet`](https://github.com/VirtualPlanetaryLaboratory/bigplanet) to store and quickly analyze the results.
