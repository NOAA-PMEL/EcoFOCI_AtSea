#!/usr/bin/env python

"""
CTDnc2odv.py

dump netcdf as odv 
information is dumped to screen and needs to be captured to a file

Usage:
-----
CTDnc2odv.py {filename} > filename.odv

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse
import os

#Science Stack
from netCDF4 import Dataset
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'

"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def get_var_atts(nchandle, var_name):
    return nchandle.variables[var_name]

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)
"""--------------------------------EPIC Routines---------------------------------------"""

def EPICdate2udunits(time1, time2):
    """
    Inputs
    ------
          time1: array_like
                 True Julian day
          time2: array_like
                 Milliseconds from 0000 GMT
    Returns
    -------
          dictionary:
            'timeint': python serial time
            'interval_min': data interval in minutes
    
    Example
    -------
    Python uses days since 0001-01-01 and a gregorian calendar

      
    Reference
    ---------
    PMEL-EPIC Conventions (misprint) says 2400000
    http://www.epic.noaa.gov/epic/eps-manual/epslib_ch5.html#SEC57 says:
    May 23 1968 is 2440000 and July4, 1994 is 2449538
              
    """
    ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
    ref_time_epic = 2440000
    
    offset = ref_time_epic - ref_time_py
    
    try:
        pytime = [None] * len(time1)

        for i, val in enumerate(time1):
            pyday = time1[i] - offset 
            pyfrac = time2[i] / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
            pytime[i] = (pyday + pyfrac)
            
    except:
        pytime = []
    
        pyday = time1 - offset 
        pyfrac = time2 / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
        pytime = (pyday + pyfrac)
    
    return pytime

def pythondate2str(pdate):
    (year,month,day) = datetime.datetime.fromordinal(int(pdate)).strftime('%Y-%m-%d').split('-')
    delta_t = pdate - int(pdate)
    dhour = str(int(np.floor(24 * (delta_t))))
    dmin = str(int(np.floor(60 * ((24 * (delta_t)) - np.floor(24 * (delta_t))))))
    dsec = str(int(np.floor(60 * ((60 * ((24 * (delta_t)) - np.floor(24 * (delta_t)))) - \
                    np.floor(60 * ((24 * (delta_t)) - np.floor(24 * (delta_t))))))))
                    
    #add zeros to time
    if len(dhour) == 1:
        dhour = '0' + dhour
    if len(dmin) == 1:
        dmin = '0' + dmin
    if len(dsec) == 1:
        dsec = '0' + dsec
                

    return(year,month,day,dhour+':'+dmin)  
        
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
    nchandle = Dataset(ncfile,'r') 
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    ncdata = ncreadfile_dic(nchandle, vars_dic.keys())
    nchandle.close()
   
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
        date_raw = pythondate2str( EPICdate2udunits(ncdata['time'][0], ncdata['time2'][0]) )       
        standard_header_val[6] = ("{0}-{1}-{2} {3}").format(date_raw[0], date_raw[1], date_raw[2], date_raw[3])
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
        
    
