"""
 Background:
 ===========
 CTD_Interp2SFC.py
 
 
 Purpose:
 ========
 Interpolate all paramters of a CTD netcdf profile from chosen depth to the surface.

 Output to original file, or to csv

 File Format:
 ============
 - works only on netcdf files (EPIC or CF?)

 (Very Long) Example Usage:
 ==========================


 History:
 ========

 Compatibility:
 ==============
 python >=3.6 
 python 2.7

"""
from __future__ import absolute_import, division, print_function

import argparse
import datetime
import os
import sys

import numpy as np
import pandas as pd
from netCDF4 import Dataset

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2018, 7, 14)
__modified__ = datetime.datetime(2018, 7, 14)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "netCDF", "meta", "header", "QC", "interp", "sfc"

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Interpolate to SFC from chosen depth for CTD files"
)
parser.add_argument(
    "ctd_file", metavar="ctd_file", type=str, help="full path to ctd file"
)
parser.add_argument(
    "depth", metavar="depth", type=int, help="depth to interpolate to sfc from"
)

args = parser.parse_args()


ncfile = args.ctd_file
df = EcoFOCI_netCDF(ncfile)
global_atts = df.get_global_atts()
nchandle = df._getnchandle_()
vars_dic = df.get_vars()
ncdata = df.ncreadfile_dic()

try:
    depth_ind = ncdata["depth"] < args.depth
except:
    depth_ind = ncdata["dep"] < args.depth

for variable in vars_dic.keys():
    if not variable in [
        "time",
        "time2",
        "dep",
        "depth",
        "P_1",
        "D_3",
        "lat",
        "latitude",
        "lon",
        "longitude",
    ]:
        nchandle.variables[variable][0, depth_ind, 0, 0] = nchandle.variables[variable][
            0, args.depth, 0, 0
        ]

addhist = "Interpolated from {} to SFC".format(args.depth)
print("adding history attribute")
if not "History" in global_atts.keys():
    histtime = datetime.datetime.utcnow()
    nchandle.setncattr(
        "History",
        "{histtime:%B %d, %Y %H:%M} UTC - {history} ".format(
            histtime=histtime, history=addhist
        ),
    )
else:
    histtime = datetime.datetime.utcnow()
    nchandle.setncattr(
        "History",
        global_atts["History"]
        + "\n"
        + "{histtime:%B %d, %Y %H:%M} UTC - {history}".format(
            histtime=histtime, history=addhist
        ),
    )

df.close()
