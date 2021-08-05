#!/usr/bin/env python

import os
import multiprocessing as mp
import sys
import subprocess as sub
import h5py
import numpy as np
import csv
from scipy import stats
from vspace import main

"""
Code for Multi-planet Module
"""


def RunVspace(InputFile,forced=False):
    main(InputFile,forced)
