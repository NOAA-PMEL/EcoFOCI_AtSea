"""
 Background:
 ===========
 CTDpNUT_ncgen.py
 
 
 Purpose:
 ========
 Creates EPIC flavored, merged .nc files downcast ctd and  nutrient data.
    Data assumes a sparse grid for nutrient data, scales it up to the full 1m grid of 
    ctd data and then matches on depth.  Finally, it writes a new file (mirrored to the 
    ctd file but with addtional variables defined by the nut config file)

 Todo: switch from EPIC to CF , copy global attributes and ctd files from CTD/Nut casts instead
    of specifying config files.

 File Format:
 ============
 - S.Bell - epic ctd and epic nut data 
 - Pavlof DB for cruise/cast metadata

 (Very Long) Example Usage:
 ==========================

 History:
 ========

 Compatibility:
 ==============
 python >=3.6 
 python 2.7 - ?

"""

from __future__ import absolute_import, division, print_function

# System Stack
import datetime
import argparse
import sys
import os
from shutil import copyfile

# Science Stack
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS
import io_utils.EcoFOCI_netCDF_write as EcF_write
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF


__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2018, 6, 14)
__modified__ = datetime.datetime(2018, 6, 14)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "netCDF", "meta", "header", "QC", "bottle", "discreet"

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Merge and archive nutrient csv data and 1m downcast data"
)
parser.add_argument(
    "CruiseID", metavar="CruiseID", type=str, help="provide the cruiseid"
)
parser.add_argument(
    "ctd_ncpath", metavar="ctd_ncpath", type=str, help="ctd netcdf directory"
)
parser.add_argument(
    "nut_ncpath", metavar="nut_ncpath", type=str, help="nutrient netcdf directory"
)
parser.add_argument(
    "output",
    metavar="output",
    type=str,
    help="full path to output folder (files will be generated there",
)
parser.add_argument(
    "config_file_name",
    metavar="config_file_name",
    type=str,
    default="",
    help="full path to config file - ctdpnut_epickeys.yaml",
)
parser.add_argument("-v", "--verbose", action="store_true", help="output messages")
parser.add_argument(
    "-csv", "--csv", action="store_true", help="output merged data as csv"
)

args = parser.parse_args()

# Get all netcdf files from mooring directory
ctd_ncfiles = [
    args.ctd_ncpath + f for f in os.listdir(args.ctd_ncpath) if f.endswith(".nc")
]
nut_ncfiles = [
    args.nut_ncpath + f for f in os.listdir(args.nut_ncpath) if f.endswith(".nc")
]

# get config file for output content
if args.config_file_name.split(".")[-1] in ["json", "pyini"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "json")
elif args.config_file_name.split(".")[-1] in ["yaml"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "yaml")
else:
    sys.exit("Exiting: config files must have .pyini, .json, or .yaml endings")


# loop through all ctd files - skip files without downcast for now
for ind, cast in enumerate(ctd_ncfiles):

    nut_cast = cast.split("/")[-1].replace("_ctd", "_nut")
    print(
        "Merging {ctdfile} and {nutfile}".format(
            ctdfile=cast, nutfile=(args.nut_ncpath + nut_cast)
        )
    )
    ###nc readin/out
    df = EcoFOCI_netCDF(cast)
    global_atts = df.get_global_atts()
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic(output="vector")
    ncdata_coords = [ncdata.pop(x, "-9999") for x in ["time", "time2", "lat", "lon"]]
    df.close()

    if "depth" in vars_dic:
        ncdata["dep"] = ncdata["depth"]

    ### read paired nut file
    try:
        ncdata_nut = {}
        dfn = EcoFOCI_netCDF(args.nut_ncpath + nut_cast)
        global_atts_nut = dfn.get_global_atts()
        vars_dic_nut = dfn.get_vars()
        ncdata_nut = dfn.ncreadfile_dic(output="vector")
        dfn.close()
    except:
        print("No matched Nutrient Data from cast:ctd{}".format(global_atts["CAST"]))
        print("Copy CTD file to output dir")
        copyfile(cast, args.output + cast.split("/")[-1])
        if args.csv:
            nc_only = pd.DataFrame.from_dict(ncdata)
            nc_only.to_csv(args.output + nut_cast.replace("nut.nc", "ctd.csv"))
        continue

    data_dic = {}
    # prep dictionary to send to netcdf gen

    try:
        data_dic.update({"dep": ncdata_nut["depth"][:].round()})
    except KeyError:
        data_dic.update({"dep": ncdata_nut["dep"][:].round()})

    # check for all variables in ctdfile
    for key in EPIC_VARS_dict.keys():
        if key in ncdata.keys():
            if args.verbose:
                print("{} as defined found in ctd nc file".format(key))
        else:
            if args.verbose:
                print("{} as defined not in ctd nc file".format(key))
    # using config file, build datadic by looping through each variable and using
    for key in EPIC_VARS_dict.keys():
        if not key in ncdata.keys():
            try:
                data_dic.update({key: ncdata_nut[key][:]})
                if args.verbose:
                    print("{} as defined found in nut nc file".format(key))
            except KeyError:
                if args.verbose:
                    print("{} as defined not in nut nc file".format(key))

    cruise = args.CruiseID.lower()

    # build complete dataframe from nuts to match to ctd
    try:
        nut_df = pd.merge(
            pd.DataFrame.from_dict(ncdata),
            pd.DataFrame.from_dict(data_dic),
            how="outer",
            on=["dep"],
        )
    except:
        print("Failed Merger - skip cast:ctd{}".format(global_atts["CAST"]))
        print("Copy CTD file to output dir")
        copyfile(cast, args.output + cast.split("/")[-1])
        if args.csv:
            nc_only = pd.DataFrame.from_dict(ncdata)
            nc_only.to_csv(args.output + nut_cast.replace("nut.nc", "mergefailed.csv"))
        continue

    if args.csv:
        nut_df.to_csv(args.output + nut_cast.replace("nut.nc", "merged.csv"))
    else:

        history = ":File created by merging {nutfile} and {ctdfile} files".format(
            nutfile=nut_cast, ctdfile=cast.split("/")[-1]
        )
        # build netcdf file - filename is castid
        ### Time should be consistent in all files as a datetime object
        # convert timestamp to datetime to epic time

        profile_name = args.output + nut_cast.replace("nut", "merged")

        ncinstance = EcF_write.NetCDF_Create_Profile(savefile=profile_name)
        ncinstance.file_create()
        ncinstance.sbeglobal_atts(
            raw_data_file=args.ctd_ncpath.split("/")[-1]
            + ","
            + args.nut_ncpath.split("/")[-1],
            CruiseID=cruise,
            Cast=cast,
        )
        ncinstance.dimension_init(depth_len=len(nut_df))
        ncinstance.variable_init(EPIC_VARS_dict)
        ncinstance.add_coord_data(
            depth=nut_df["dep"].values,
            latitude=ncdata_coords[2],
            longitude=ncdata_coords[3],
            time1=ncdata_coords[0],
            time2=ncdata_coords[1],
        )
        ncinstance.add_data(EPIC_VARS_dict, data_dic=nut_df.to_dict("list"))
        ncinstance.add_history(history)
        ncinstance.close()
