#!/usr/bin/env python

"""
CTDnc2odv.py

dump netcdf as odv 
information is dumped to screen and needs to be captured to a file

Usage:
-----
CTDnc2odv.py {filename} > filename.odv


History:
--------

2017-05-09: SBELL - migrate to consistent placement of subroutines for nc read and time tools

"""

#System Stack
import datetime
import argparse
import os

#Science Stack
from netCDF4 import Dataset
import numpy as np

#User Stack
from calc.EPIC2Datetime import EPIC2Datetime
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'


"""---------------------------------- Main --------------------------------------------"""

parser = argparse.ArgumentParser(description='Converts FOCI/EPIC .nc CTD cast files to .odv spreadsheets')
parser.add_argument('infile', metavar='infile', type=str, help='input file path')
parser.add_argument("-EPIC",'--epic', nargs='+', type=str, help='list of desired epic variables')


args = parser.parse_args()

ncpath = args.infile
# Get all netcdf files from mooring directory
ncfiles = [f for f in os.listdir(args.infile) if f.endswith('.nc')]

for ncfile in ncfiles:
    ncfile = ncpath + ncfile
    ###nc readin/out
    df = EcoFOCI_netCDF(ncfile)
    global_atts = df.get_global_atts()
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    df.close()
   
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
        standard_header_val[6] = "2020-12-12-25 00:00"
    ###screen output

    header = []

    #if epic list is supplied, else all
    if args.epic:
        for dindex in range(0,len(ncdata['dep']),1):
            val = []
            for var in sorted(args.epic):
                if (var == 'lat') or (var =='lon') or (var == 'time') or (var == 'time2'): 
                    #handle non depth dimensions seperaty
                    continue
                elif var == 'dep':
                    header = header + ['dep']
                    try:
                        val = val + [str(ncdata['dep'][dindex])]
                    except:
                        val = val + []
                else:
                    header = header + [str(var)]
                    try:
                        val = val + [str(ncdata[var][0,dindex,0,0])]
                    except:
                        val = val + []
            if dindex == 0:
                print "\t".join(standard_header + header)        

            print "\t".join(standard_header_val + val)
    else:
        for dindex in range(0,len(ncdata['dep']),1):
            val = []
            for var in sorted(ncdata.keys()):
                if (var == 'lat') or (var =='lon') or (var == 'time') or (var == 'time2'): 
                    #handle non depth dimensions seperaty
                    continue
                elif var == 'dep':
                    header = header + ['dep']
                    val = val + [str(ncdata['dep'][dindex])]
                else:
                    header = header + [str(var)]
                    val = val + [str(ncdata[var][0,dindex,0,0])]
            if dindex == 0:
                print "\t".join(standard_header + header)        

            print "\t".join(standard_header_val + val)
        
    
