#!/usr/bin/env python

"""
 SCS_entire_shptrack2nc.py

 History:
 --------

"""

import argparse
import datetime
import os

import numpy as np
import pandas as pd
from netCDF4 import date2num, num2date

import io_utils.ConfigParserLocal as ConfigParserLocal
import io_utils.EcoFOCI_netCDF_write as EcF_write

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2017, 4, 12)
__modified__ = datetime.datetime(2017, 4, 12)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "gpx", "shiptrack"


def convert_dms_to_dec(value, dir):
    dPos = str(value).find(".")

    mPos = dPos - 2
    ePos = dPos

    main = float(str(value)[:mPos])
    min1 = float(str(value)[mPos:])

    # 	print "degrees:'%s', minutes:'%s'\n" % (main, min1)

    newval = float(main) + float(min1) / float(60)

    if dir == "W":
        newval = -newval
    elif dir == "S":
        newval = -newval

    return newval


"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Convert SCS GPGGA gps files to .nc files")
parser.add_argument("inpath", type=str, help="path to data files")
parser.add_argument("ConfigFile", type=str, help="full path to nc config file")
args = parser.parse_args()

# Get all files from given directory
flist = [args.inpath + f for f in os.listdir(args.inpath) if "GPGGA" in f]

lat = lon = timestamp = []
for fin in flist:
    print("{currentfile}".format(currentfile=fin))
    try:
        rawdata = pd.read_csv(fin, header=None, error_bad_lines=False)
        lat = lat + [
            convert_dms_to_dec(v1, v2)
            for v1, v2 in zip(rawdata[4].values, rawdata[5].values)
        ]
        lon = lon + [
            convert_dms_to_dec(v1, v2)
            for v1, v2 in zip(rawdata[6].values, rawdata[7].values)
        ]
        timestamp = timestamp + [
            (pd.to_datetime(v1 + " " + v2[:-4], format="%m/%d/%Y %H:%M:%S"))
            .to_pydatetime()
            .isoformat()
            for v1, v2 in zip(rawdata[0].values, rawdata[1].values)
        ]
        print(len(lat), len(lon), len(timestamp))
    except:
        print("something failed in file {0}".format(fin))

data = pd.DataFrame({"DateTime": timestamp, "latitude": lat, "longitude": lon})
data.set_index(pd.DatetimeIndex(data["DateTime"]), inplace=True)
data["time"] = [
    date2num(x[1], "hours since 1900-01-01T00:00:00Z") for x in enumerate(data.index)
]

EPIC_VARS_dict = ConfigParserLocal.get_config(args.ConfigFile, "yaml")

# create new netcdf file
ncinstance = EcF_write.NetCDF_Create_Profile_Ragged1D(
    savefile=args.inpath + "shiptrack.nc"
)
ncinstance.file_create()
ncinstance.sbeglobal_atts(
    raw_data_file="", History="File Created from SCS GPPGA GPS data."
)
ncinstance.dimension_init(recnum_len=len(data))
ncinstance.variable_init(EPIC_VARS_dict)
ncinstance.add_coord_data(recnum=range(1, len(data) + 1))
ncinstance.add_data(EPIC_VARS_dict, data_dic=data,
                    missing_values=np.nan, pandas=True)
ncinstance.close()
