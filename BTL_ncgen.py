"""
 Background:
 ===========
 BTL_ncgen.py
 
 
 Purpose:
 ========
 Creates EPIC flavored .nc files for bottle (sbe updcast discrete) data
 Todo: switch from EPIC to CF

 File Format:
 ============
 - S.Bell - combined seabird btl report output
 - Pavlof DB for cruise/cast metadata

 (Very Long) Example Usage:
 ==========================

 'python BTL_ncgen.py DY1707 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/dy1707l1.report_btl 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/ /Users/bell/Programs/Python/EcoFOCI_AtSea/config_files/btl_epickeys.yaml'

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
import sys

import numpy as np
import pandas as pd
from netCDF4 import Dataset

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
import io_utils.EcoFOCI_netCDF_write as EcF_write
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2018, 6, 14)
__modified__ = datetime.datetime(2018, 6, 14)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "netCDF", "meta", "header", "QC", "bottle", "discreet"

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Merge and archive nutrient csv data and bottle data"
)
parser.add_argument(
    "CruiseID", metavar="CruiseID", type=str, help="provide the cruiseid"
)
parser.add_argument(
    "btlpath", metavar="btlpath", type=str, help="full path to .report_btl"
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
    help="full path to config file - bottle_epickeys.yaml",
)

args = parser.parse_args()

### Read BTL Report file...
# Bottle Report file obtained by concatenating bottle files without headers
reportdf = pd.read_csv(args.btlpath, delimiter="\s+", parse_dates=[["date", "time"]])

print("Btl Report Header Summary:")
print(reportdf.info())

# strip ctd from cast name and make integer
try:
    reportdf["CastNum"] = [
        int(x.lower().split("ctd")[-1]) for y, x in reportdf.cast.iteritems()
    ]
except ValueError:
    sys.exit("Exiting: Report file doesn't have casts named as expected... ctdxxx")

# make a cast_niskin column to index on
reportdf["Cast_Niskin"] = [
    str(x["CastNum"]).zfill(3) + "_" + str(x["nb"]).zfill(2)
    for y, x in reportdf.iterrows()
]
reportdf.sort_values(["Cast_Niskin"], inplace=True)

# Groupby Cast and write to file
# print out to screen data not saved due to lack of cast info (CTD)
# missing data is automatically excluded (NA groups)
gb = reportdf.groupby("cast")

# get config file for output content
if args.config_file_name.split(".")[-1] in ["json", "pyini"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "json")
elif args.config_file_name.split(".")[-1] in ["yaml"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "yaml")
else:
    sys.exit("Exiting: config files must have .pyini, .json, or .yaml endings")


for i, cast in enumerate(gb.groups):
    tdata = gb.get_group(cast).sort_values("CastNum")

    data_dic = {}
    # prep dictionary to send to netcdf gen
    data_dic.update({"time": tdata["date_time"].values})
    try:
        data_dic.update({"dep": tdata["PrDM"].values})
    except KeyError:
        data_dic.update({"dep": tdata["PrSM"].values})

    # using config file, build datadic by looping through each variable and using
    # 'sbe_label'
    for key in EPIC_VARS_dict.keys():
        if EPIC_VARS_dict[key]["sbe_label"]:
            try:
                data_dic.update({key: tdata[EPIC_VARS_dict[key]["sbe_label"]].values})
                print(
                    "{} as defined found in btl file".format(
                        EPIC_VARS_dict[key]["sbe_label"]
                    )
                )
            except KeyError:
                print(
                    "{} as defined not in btl file".format(
                        EPIC_VARS_dict[key]["sbe_label"]
                    )
                )
        else:
            print("{} as defined not in config file".format(key))

    cruise = args.CruiseID.lower()
    cast = list(tdata.groupby("cast").groups.keys())[0]
    profile_name = args.output + cruise + cast.replace("ctd", "c") + "_btl.nc"

    history = "File created by archiving bottle report files"
    # build netcdf file - filename is castid
    ### Time should be consistent in all files as a datetime object
    # convert timestamp to datetime to epic time
    data_dic["time"] = pd.to_datetime(data_dic["time"], format="%Y%m%d %H:%M:%S")
    time_datetime = [x.to_pydatetime() for x in data_dic["time"]]
    time1, time2 = np.array(Datetime2EPIC(time_datetime), dtype="f8")

    ncinstance = EcF_write.NetCDF_Create_Profile(savefile=profile_name)
    ncinstance.file_create()
    ncinstance.sbeglobal_atts(
        raw_data_file=args.btlpath.split("/")[-1], CruiseID=cruise, Cast=cast
    )
    ncinstance.dimension_init(depth_len=len(tdata))
    ncinstance.variable_init(EPIC_VARS_dict)
    ncinstance.add_coord_data(
        depth=data_dic["dep"],
        latitude=1e35,
        longitude=1e35,
        time1=time1[0],
        time2=time2[0],
    )
    ncinstance.add_data(EPIC_VARS_dict, data_dic=data_dic)
    ncinstance.add_history(history)
    ncinstance.close()
