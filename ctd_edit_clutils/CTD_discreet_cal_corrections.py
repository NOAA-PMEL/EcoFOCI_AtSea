#!/usr/bin/env python

"""

 Background:
 ===========
 CTD_discreet_cal_corrections.py

 Purpose:
 ========
 Apply salinity or oxygen calibration corrections to CTD data

 USAGE:
 ========
 python CTD_discreet_cal_corrections.py {data} --secondary_oxygen {linear_correction_slope linear_correction_offset}
 python CTD_discreet_cal_corrections.py {data} --secondary_salinity {offset_correction}
 
 History:
 ========
 2019-08-15: Python 3 print statments and f-strings

 Compatibility:
 ==============
 python >=3.6
 python 2.7 - not supported

"""
# System Stack
import datetime
import argparse
import os
import sys

# must be python 3.6 or greater
try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    sys.exit("Must be running python 3.6 or greater")


# Science Stack
from netCDF4 import Dataset
import numpy as np

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2014, 10, 30)
__modified__ = datetime.datetime(2014, 10, 30)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "CTD", "SeaWater", "Cruise", "derivations"

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
    nchandle.variables[var_name][:] = val[:]
    return


"""----------------------------- MAIN -------------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Apply corrections from Discreet oxygen or salinity samples"
)
parser.add_argument(
    "DataPath", metavar="DataPath", type=str, help="full path to directory for cruise"
)
parser.add_argument(
    "--primary_oxygen",
    nargs="+",
    type=float,
    help="apply linear correction to primary oxygen",
)
parser.add_argument(
    "--secondary_oxygen",
    nargs="+",
    type=float,
    help="apply linear correction to secondary oxygen",
)
parser.add_argument(
    "--primary_salinity", type=float, help="apply offset correction to primary salinity"
)
parser.add_argument(
    "--secondary_salinity",
    type=float,
    help="apply offset correction to secondary salinity",
)
parser.add_argument(
    "--fluorometer",
    type=float,
    help="apply offset correction to fluorometer (0.0 - deep noise)",
)

args = parser.parse_args()

### get all .nc files from chosen directory
full_path = [args.DataPath + x for x in os.listdir(args.DataPath) if x.endswith(".nc")]

if args.primary_oxygen:  # O_65
    for ifile, ncfile in enumerate(full_path):
        print(f"Working on file {ncfile} \n")
        ###nc readin
        nchandle = Dataset(ncfile, "a")
        global_atts = get_global_atts(nchandle)
        vars_dic = get_vars(nchandle)
        data = ncreadfile_dic(nchandle, ["O_65"])
        O2corr = (data["O_65"] * args.primary_oxygen[0]) + args.primary_oxygen[1]
        O2corr[0, data["O_65"][0, :, 0, 0] >= 1e10, 0, 0] = 1e35

        repl_var(nchandle, "O_65", O2corr)

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1, 10):
            if ("PROG_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "PROG_CMNT0" + str(i + 1), global_atts["PROG_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "PROG_CMNT01", __file__.split("/")[-1] + " v" + __version__
                )
            if ("EDIT_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "EDIT_CMNT0" + str(i + 1), global_atts["EDIT_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "EDIT_CMNT01",
                    "Primary Oxygen Cal Factor of: "
                    + str(args.primary_oxygen[0])
                    + "x + "
                    + str(args.primary_oxygen[1])
                    + " applied",
                )
        nchandle.close()

if args.secondary_oxygen:  # CTDOXY_4221
    for ifile, ncfile in enumerate(full_path):
        print(f"Working on file {ncfile} \n")
        ###nc readin
        nchandle = Dataset(ncfile, "a")
        global_atts = get_global_atts(nchandle)
        vars_dic = get_vars(nchandle)
        data = ncreadfile_dic(nchandle, ["CTDOXY_4221"])
        O2corr = (
            data["CTDOXY_4221"] * args.secondary_oxygen[0]
        ) + args.secondary_oxygen[1]
        O2corr[0, data["CTDOXY_4221"][0, :, 0, 0] >= 1e10, 0, 0] = 1e35

        repl_var(nchandle, "CTDOXY_4221", O2corr)

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1, 10):
            if ("PROG_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "PROG_CMNT0" + str(i + 1), global_atts["PROG_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "PROG_CMNT01", __file__.split("/")[-1] + " v" + __version__
                )
            if ("EDIT_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "EDIT_CMNT0" + str(i + 1), global_atts["EDIT_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "EDIT_CMNT01",
                    "Secondary Oxygen Cal Factor of: "
                    + str(args.secondary_oxygen[0])
                    + "x + "
                    + str(args.secondary_oxygen[1])
                    + " applied",
                )

        nchandle.close()

if args.primary_salinity:  # S_41
    for ifile, ncfile in enumerate(full_path):
        print(f"Working on file {ncfile} \n")
        ###nc readin
        nchandle = Dataset(ncfile, "a")
        global_atts = get_global_atts(nchandle)
        vars_dic = get_vars(nchandle)
        data = ncreadfile_dic(nchandle, ["S_41"])
        repl_var(nchandle, "S_41", data["S_41"] + args.primary_salinity)

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1, 10):
            if ("PROG_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "PROG_CMNT0" + str(i + 1), global_atts["PROG_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "PROG_CMNT01", __file__.split("/")[-1] + " v" + __version__
                )
            if ("EDIT_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "EDIT_CMNT0" + str(i + 1), global_atts["EDIT_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "EDIT_CMNT01",
                    "Primary Salinity Cal Factor of: "
                    + str(args.primary_salinity)
                    + " applied",
                )

        nchandle.close()

if args.secondary_salinity:  # S_42
    for ifile, ncfile in enumerate(full_path):
        print(f"Working on file {ncfile} \n")
        ###nc readin
        nchandle = Dataset(ncfile, "a")
        global_atts = get_global_atts(nchandle)
        vars_dic = get_vars(nchandle)
        data = ncreadfile_dic(nchandle, ["S_42"])
        repl_var(nchandle, "S_42", data["S_42"] + args.secondary_salinity)

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1, 10):
            if ("PROG_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "PROG_CMNT0" + str(i + 1), global_atts["PROG_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "PROG_CMNT01", __file__.split("/")[-1] + " v" + __version__
                )
            if ("EDIT_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "EDIT_CMNT0" + str(i + 1), global_atts["EDIT_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "EDIT_CMNT01",
                    "Secondary Salinity Cal Factor of: "
                    + str(args.secondary_salinity)
                    + " applied",
                )

        nchandle.close()

if args.fluorometer:  # fWS_973, or F_903
    for ifile, ncfile in enumerate(full_path):
        print(f"Working on file {ncfile} \n")
        ###nc readin
        nchandle = Dataset(ncfile, "a")
        global_atts = get_global_atts(nchandle)
        vars_dic = get_vars(nchandle)
        try:
            data = ncreadfile_dic(nchandle, ["fWS_973"])
            repl_var(nchandle, "fWS_973", data["fWS_973"] + args.fluorometer)
        except:
            try:
                data = ncreadfile_dic(nchandle, ["F_903"])
                repl_var(nchandle, "F_903", data["F_903"] + args.fluorometer)
            except:
                print("No valid Fluorometer key - F_903 or fWS_973 found")

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1, 10):
            if ("PROG_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "PROG_CMNT0" + str(i + 1), global_atts["PROG_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "PROG_CMNT01", __file__.split("/")[-1] + " v" + __version__
                )
            if ("EDIT_CMNT0" + str(i)) in global_atts.keys():
                nchandle.setncattr(
                    "EDIT_CMNT0" + str(i + 1), global_atts["EDIT_CMNT0" + str(i)]
                )
            else:
                nchandle.setncattr(
                    "EDIT_CMNT01",
                    "Fluorometer offset of: " + str(args.fluorometer) + " applied",
                )

        nchandle.close()
