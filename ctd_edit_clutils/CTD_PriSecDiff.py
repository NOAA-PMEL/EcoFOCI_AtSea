#!/usr/bin/env python

"""
 Background:
 ===========
 CTD_PriSecDiff.py
 
 
 Purpose:
 ========
 Calculate the depth averaged difference between primary and secondary salinity/temperature and report statistics
 
 History:
 ========


 Compatibility:
 ==============
 python >=3.6 - **Tested**
 python 2.7 - may work but not supported
"""

import argparse
import datetime
import os

import numpy as np
from netCDF4 import Dataset

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2019, 2, 20)
__modified__ = datetime.datetime(2019, 2, 20)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "netCDF", "meta", "header"


"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()

    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)

    return g_atts


def get_vars(nchandle):
    return nchandle.variables


def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params):
        if v in nchandle.variables.keys():  # check for nc variable
            data[v] = nchandle.variables[v][:]

        else:  # if parameter doesn't exist fill the array with zeros
            data[v] = None
    return data


def repl_var(nchandle, var_name, val):
    nchandle.variables[var_name][0, :, 0, 0] = val
    return


"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(description="add a variable to a .nc file")
parser.add_argument(
    "sourcedir", metavar="sourcedir", type=str, help="path to .nc files"
)

args = parser.parse_args()

ctd_data_files = [x for x in os.listdir(args.sourcedir) if x.endswith(".nc")]

for count, ncfile in enumerate(
    sorted(ctd_data_files)
):  # cycle through all available files for an id

    ###nc readin
    nchandle = Dataset(args.sourcedir + ncfile, "a")
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    data = ncreadfile_dic(nchandle, vars_dic.keys())

    inst_dif = data["S_41"][0, :, 0, 0] - data["S_42"][0, :, 0, 0]
    inst_dif = data["T_20"][0, :, 0, 0] - data["T2_35"][0, :, 0, 0]

    print(
        "{file}: Salinity - mean:{smean}, std:{sstd}; Temperature - mean:{tmean}, std:{tstd}".format(
            file=ncfile,
            smean=np.nanmean(inst_dif),
            sstd=np.nanstd(inst_dif),
            tmean=np.nanmean(inst_dif),
            tstd=np.nanstd(inst_dif),
        )
    )

    nchandle.close()
