#!/usr/bin/env python

"""
CTD_andbtl_nc2odv.py

dump netcdf bottle and ctd files as as odv

Usage:
-----
python CTD_andbtl_nc2odv.py /Users/bell/Data_Local/FOCI/ecoraid/2014/CTDcasts/kh1401/working/ --btl_dir /Users/bell/Data_Local/FOCI/ecoraid/2014/CTDcasts/kh1401/working/ > kh1401_odv.txt

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
    nchandle = Dataset(ncfile,'r') 
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    ncdata = ncreadfile_dic(nchandle, vars_dic.keys())
    nchandle.close()
    #btl file data assuming same naming convention
    missing_btl = False
    try:
        nchandle = Dataset(btl_ncfile,'r') 
        global_atts_btl = get_global_atts(nchandle)
        vars_dic_btl = get_vars(nchandle)
        ncdata_btl = ncreadfile_dic(nchandle, vars_dic_btl.keys())
        nchandle.close()
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
        date_raw = pythondate2str( EPICdate2udunits(ncdata['time'][0], ncdata['time2'][0]) )       
        standard_header_val[6] = ("{0}-{1}-{2} {3}").format(date_raw[0], date_raw[1], date_raw[2], date_raw[3])
    except ValueError:
        standard_header_val[6] = "2020-12-12-25 00:00"
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


