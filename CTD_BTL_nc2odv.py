#!/usr/bin/env python

"""
CTD_andbtl_nc2odv.py

dump netcdf bottle and ctd files as as odv

Usage:
-----
python CTD_andbtl_nc2odv.py /Users/bell/Data_Local/FOCI/ecoraid/2014/CTDcasts/kh1401/working/ --btl_dir /Users/bell/Data_Local/FOCI/ecoraid/2014/CTDcasts/kh1401/working/ > kh1401_odv.txt

History:
--------

2017-05-09: SBELL - migrate to consistent placement of subroutines for nc read and time tools
"""

import argparse
import datetime
import os

import numpy as np
from netCDF4 import Dataset

from calc.EPIC2Datetime import EPIC2Datetime
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2014, 5, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'
        
"""---------------------------------- Main --------------------------------------------"""

# arg parse command line arguments
parser = argparse.ArgumentParser(description='Converts FOCI/EPIC .nc CTD files to .odv friendly spreadsheets.  A flag is available to include bottle/discreet files as well')
parser.add_argument('ctd_dir', metavar='ctd_dir', type=str, help='input file path to ctd data')
parser.add_argument('--btl_dir', nargs='+', type=str, help='(optional) input file path to btl data')

args = parser.parse_args()


# Get all netcdf files from mooring directory
ctd_ncpath = args.ctd_dir
ctd_ncfiles = [f for f in os.listdir(ctd_ncpath) if f.endswith('_ctd.nc')]

if args.btl_dir:
    Btl_Vars = ['BTL_103','SI_188','PO4_186','NH4_189','NO2_184','NO3_182']
    Btl_vert = 'dep'
    Btl_vert = 'depth'

    btl_ncpath = args.btl_dir[0]
    btl_ncfiles = [f for f in os.listdir(btl_ncpath) if f.endswith('nut.nc')]

for ncfile in ctd_ncfiles:
    btl_ncfile = btl_ncpath + "nut".join(ncfile.split('ctd'))
    ncfile = ctd_ncpath + ncfile

    ###nc readin/out
    df = EcoFOCI_netCDF(ncfile)
    global_atts = df.get_global_atts()
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    df.close()

    #btl file data assuming same naming convention
    missing_btl = False
    try:
        df = EcoFOCI_netCDF(btl_ncfile)
        global_atts_btl = df.get_global_atts()
        vars_dic_btl = df.get_vars()
        ncdata_btl = df.ncreadfile_dic()
        df.close()
    except:
        #print "Missing btl file {0}".format(btl_ncfile)
        missing_btl = True
           
    standard_header = ['cruise','cast','type','station_number','station_name','ctd_type',
                        'yyyy-mm-dd hh:mm','longitude [degrees east]','latitude [degrees north]','Bot. Depth [m]']
    standard_header_val = ['','','1','','','std','','','','']

    #from meta information
    if global_atts.has_key('CRUISE'):
        standard_header_val[0] = global_atts['CRUISE']
    else:
        standard_header_val[0] = ''

    if global_atts.has_key('CAST'):
        standard_header_val[1] = global_atts['CAST']
    else:
        standard_header_val[1] = ''

    if global_atts.has_key('STATION_NUMBER'):
        standard_header_val[3] = global_atts['STATION_NUMBER']
    else:
        standard_header_val[3] = 'no_number'
    
    if global_atts.has_key('STATION_NAME'):
        standard_header_val[4] = global_atts['STATION_NAME']
    else:
        standard_header_val[4] = 'no_name'
    
    if global_atts.has_key('WATER_DEPTH'):
        standard_header_val[9] = str(global_atts['WATER_DEPTH'])
    else:
        standard_header_val[9] = ''
    
    #from dimensions
    standard_header_val[7] = str(-1 * ncdata['lon'][0])       
    standard_header_val[8] = str(ncdata['lat'][0])
    try:       
        date_raw = EPIC2Datetime([ncdata['time'][0]], [ncdata['time2'][0]])[0]      
        standard_header_val[6] = ("{:%Y-%m-%d %H:%M}").format(date_raw)
    except ValueError:
        standard_header_val[6] = "2020-12-25 00:00"
    ###screen output

    header = []
    ctd2btl_depthmap = {}
    for dindex in range(0,len(ncdata['dep']),1):
        val = []
        for var in sorted(ncdata.keys()):
            if (var == 'lat') or (var =='lon') or (var == 'time') or (var == 'time2'): 
                #handle non depth dimensions seperaty
                continue
            elif var == 'dep':
                header = header + ['dep']
                val = val + [str(ncdata['dep'][dindex])]
                #find associated btl data
                try:
                    if ncdata['dep'][dindex] in np.round(ncdata_btl[Btl_vert]):
                        ctd2btl_depthmap[dindex] = np.where(np.round(ncdata_btl[Btl_vert])==ncdata['dep'][dindex])[0][0]
                except:
                    pass
            else:
                header = header + [str(var)]
                val = val + [str(ncdata[var][0,dindex,0,0])]
        if missing_btl == False:
            for var in sorted(ncdata_btl.keys()):
                if (var in Btl_Vars):
                    header = header + [str(var)]
                    try:
                        bindex = ctd2btl_depthmap[dindex]
                        val = val + [str(ncdata_btl[var][0,bindex,0,0])]
                    except:
                        val = val + ['']
                else:
                    continue
        if dindex == 0:
            print "\t".join(standard_header + header)        

        print "\t".join(standard_header_val + val)


