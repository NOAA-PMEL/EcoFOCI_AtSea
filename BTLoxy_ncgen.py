"""
 Background:
 ===========
 Nut_ncgen.py
 
 
 Purpose:
 ========
 Creates EPIC flavored .nc files for bottle (oxygen) data
 Todo: switch from EPIC to CF

 File Format:
 ============
 - E.Wisegarver - oxygen csv output
 - S.Bell - combined seabird btl report output
 - Pavlof DB for cruise/cast metadata

 (Very Long) Example Usage:
 ==========================

 'python BTLoxy_ncgen.py DY1707 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/dy1707l1.report_btl 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/DiscreteOxygen/DY1707\ Oxygen\ Data.csv 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/ /Users/bell/Programs/Python/EcoFOCI_AtSea/config_files/nut_uml_epickeys.yaml'

 History:
 ========

 Compatibility:
 ==============
 python >=3.6 
 python 2.7 

"""
import warnings

# remove the numpy/pandas/cython warnings
warnings.filterwarnings(action="ignore", message="numpy.dtype size changed,")

# System Stack
import datetime
import argparse
import sys

# Science Stack
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS
import io_utils.EcoFOCI_netCDF_write as EcF_write


__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2018, 7, 14)
__modified__ = datetime.datetime(2018, 7, 14)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "netCDF", "meta", "header", "QC", "bottle", "discreet", "oxygen"

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Merge and archive oxygen csv data and bottle data"
)
parser.add_argument(
    "CruiseID", metavar="CruiseID", type=str, help="provide the cruiseid"
)
parser.add_argument(
    "btlpath", metavar="btlpath", type=str, help="full path to .report_btl"
)
parser.add_argument(
    "oxypath", metavar="oxypath", type=str, help="full path to oxygen csv file"
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
    help="full path to config file - btloxy_config.yaml",
)
parser.add_argument("--cf", action="store_true", help="make cf compliant netcdf files")

args = parser.parse_args()

### Read oxygen file - processed by E. Weisgarver and
# Bottle Report file obtained by concatenating bottle files without headers
ndf = pd.read_csv(args.oxypath, sep="\t|,", engine="python")
ndf.rename(
    index=str,
    columns={"Cast": "cast", "Niskin": "niskin", "Niskin": "niskin"},
    inplace=True,
)

print("Oxygen Header Summary:")
print(ndf.info())

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
print("Matching on Cast/Niskin pair.")
ndf["Cast_Niskin"] = [
    str(int(x["cast"])).zfill(3) + "_" + str(int(x["niskin"])).zfill(2)
    for y, x in ndf.iterrows()
]
reportdf["Cast_Niskin"] = [
    str(x["CastNum"]).zfill(3) + "_" + str(x["nb"]).zfill(2)
    for y, x in reportdf.iterrows()
]

###three potential merged results
# Matching Btl and Nut file
# No Btl - yes nut (no ctd information for this nut value...)
# Yes Btl - no nut
temp = pd.merge(ndf, reportdf, on="Cast_Niskin", how="outer")
temp.sort_values(["Cast_Niskin"], inplace=True)

# Groupby Cast and write to file
# print out to screen data not saved due to lack of cast info (CTD)
# missing data is automatically excluded (NA groups)

# hack - both dataframes have 'cast' use the one from *.report_btl
gb = temp.groupby("cast_x")

# get config file for output content
if args.config_file_name.split(".")[-1] in ["json", "pyini"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "json")
elif args.config_file_name.split(".")[-1] in ["yaml"]:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name, "yaml")
else:
    sys.exit("Exiting: config files must have .pyini, .json, or .yaml endings")

if args.cf:
    # ragged array, only time
    for i, cast in enumerate(gb.groups):
        tdata = gb.get_group(cast).sort_values("CastNum")

        data_dic = {}
        # prep dictionary to send to netcdf gen
        data_dic.update({"time": tdata["date_time"].values})
        data_dic.update({"dep": tdata["PrDM"].values})
        try:
            data_dic.update({"BTL_OXY": tdata['"O2 uM/l"'].values})
        except:
            print(
                'O2 field skipped as no column match to "O2 uM/l" - remove comma if in string'
            )
        data_dic.update({"BTLID": tdata["nb"].values})

        cruise = args.CruiseID.lower()
        cast = list(tdata.groupby("cast_y").groups.keys())[0]
        profile_name = (
            args.output + cruise + cast.lower().replace("ctd", "c") + "_oxy.nc"
        )

        history = "File created by merging oxygen analysis and bottle report files"
        # build netcdf file - filename is castid
        ### Time should be consistent in all files as a datetime object
        # convert timestamp to datetime to epic time
        data_dic["time_temp"] = pd.to_datetime(
            data_dic["time"], format="%Y%m%d %H:%M:%S"
        )
        data_dic["time"] = [
            date2num(x[1], "hours since 1900-01-01T00:00:00Z")
            for x in enumerate(data_dic["time_temp"])
        ]

else:
    # 4 dimensional (t,z,y,x)
    for i, cast in enumerate(gb.groups):
        tdata = gb.get_group(cast).sort_values("CastNum")

        data_dic = {}
        # prep dictionary to send to netcdf gen
        data_dic.update({"time": tdata["date_time"].values})
        data_dic.update({"dep": tdata["PrDM"].values})
        try:
            data_dic.update({"BO_61": tdata['"O2 uM/l"'].values})
        except:
            print(
                'O2 field skipped as no column match to "O2 uM/l" - remove comma if in string'
            )
        data_dic.update({"BTL_103": tdata["nb"].values})

        cruise = args.CruiseID.lower()
        try:
            cast = list(tdata.groupby("cast_y").groups.keys())[0]
        except:
            print(
                "Oxygen Sample but no Btl Report - likely a bucket sample. Modify {cast} in bottle report".format(
                    cast=cast
                )
            )
            continue
        profile_name = (
            args.output + cruise + cast.lower().replace("ctd", "c") + "_oxy.nc"
        )

        history = "File created by merging oxygen analysis and bottle report files"
        # build netcdf file - filename is castid
        ### Time should be consistent in all files as a datetime object
        # convert timestamp to datetime to epic time
        data_dic["time"] = pd.to_datetime(data_dic["time"], format="%Y%m%d %H:%M:%S")
        time_datetime = [x.to_pydatetime() for x in data_dic["time"]]
        time1, time2 = np.array(Datetime2EPIC(time_datetime), dtype="f8")

        ncinstance = EcF_write.NetCDF_Create_Profile(savefile=profile_name)
        ncinstance.file_create()
        ncinstance.sbeglobal_atts(
            raw_data_file=args.oxypath.split("/")[-1], CruiseID=cruise, Cast=cast
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
