"""
 Background:
 ===========
 CTDpNUT_ncgen.py
 
 
 Purpose:
 ========
 Creates EPIC flavored, merged .nc files downcast ctd and  nutrient data
 Todo: switch from EPIC to CF

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

#System Stack
import datetime
import argparse
import sys
import os

#Science Stack
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS
import io_utils.EcoFOCI_netCDF_write as EcF_write
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2018, 6, 14)
__modified__ = datetime.datetime(2018, 6, 14)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet'

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Merge and archive nutrient csv data and bottle data')
parser.add_argument('CruiseID', 
    metavar='CruiseID', 
    type=str, 
    help='provide the cruiseid')
parser.add_argument('ctd_ncpath', 
    metavar='ctd_ncpath', 
    type=str, 
    help='ctd netcdf directory')
parser.add_argument('nut_ncpath', 
    metavar='nut_ncpath', 
    type=str, 
    help='nutrient netcdf directory')
parser.add_argument('output', 
    metavar='output', 
    type=str, 
    help='full path to output folder (files will be generated there')
parser.add_argument('config_file_name', 
    metavar='config_file_name', 
    type=str,
    default='', 
    help='full path to config file - ctdpnut_epickeys.yaml')

args = parser.parse_args()

# Get all netcdf files from mooring directory
ctd_ncfiles = [args.ctd_ncpath + f for f in os.listdir(args.ctd_ncpath) if f.endswith('.nc')]
nut_ncfiles = [args.nut_ncpath + f for f in os.listdir(args.nut_ncpath) if f.endswith('.nc')]

#loop through all ctd files - skip files without downcast for now
for ind,cast in enumerate(ctd_ncfiles):
    
    ###nc readin/out
    df = EcoFOCI_netCDF(cast)
    global_atts = df.get_global_atts()
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    df.close()

    ### read paired nut file
    try:
        dfn = EcoFOCI_netCDF(nut_ncfiles[ind])
        global_atts_nut = dfn.get_global_atts()
        vars_dic_nut = dfn.get_vars()
        ncdata_nut = dfn.ncreadfile_dic()
        dfn.close()
    except:
        print("No matched Nutrient Data from cast:ctd{}".format(global_atts['CAST']))