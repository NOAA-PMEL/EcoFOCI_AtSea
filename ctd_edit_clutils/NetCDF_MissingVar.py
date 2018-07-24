#!/usr/bin/env python

"""
 Background:
 ===========
 NetCDF_MissingVar.py
 
 
 Purpose:
 ========
 Replaces designated variable (currently in EPIC Format .nc files) with 1e+35 but
    only requires name of variable to work so can be run on non-epic vars as well
 
 Adds additional History:
 
 Usage:
 ======
 NetCDF_MissingVar.py -> /path/to/data/, {optional file1}, {file 2}, {file n}
 
 History:
 ========

 Compatibility:
 ==============
 python >=3.6? - untested
 python 2.7


"""

#System Stack
import datetime
import os
import sys
import argparse

#Science Stack
from netCDF4 import Dataset
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 1, 29)
__modified__ = datetime.datetime(2018, 7, 24)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC'

"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def repl_var(nchandle, var_name, val=1e35):
    nchandle.variables[var_name][:] = np.ones_like(nchandle.variables[var_name][:]) * val
    return
    

    
"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Replace EPIC Variable with 1e35 for all depths')
parser.add_argument('inputdir', metavar='inputdir', type=str, help='full path to file')
parser.add_argument('VariableName', metavar='VariableName', type=str, help='EPIC Key Code')

args = parser.parse_args()

user_var = args.VariableName

filein = args.inputdir

print "Working on file %s \n" % filein
###nc readin
nchandle = Dataset(filein,'a')
global_atts = get_global_atts(nchandle)
vars_dic = get_vars(nchandle)

if not user_var in vars_dic.keys():
    print "Variable not in EPIC file: %s      Exiting" % filein
    nchandle.close()
    sys.exit()
else:
    repl_var(nchandle, user_var, val=1e35)

    addhist="Removed {} from datastream".format(args.VariableName)
    print("adding history attribute")
    if not 'History' in global_atts.keys():
        histtime=datetime.datetime.utcnow()
        nchandle.setncattr('History','{histtime:%B %d, %Y %H:%M} UTC - {history} '.format(
                        histtime=histtime,
                        history=addhist))
    else:
        histtime=datetime.datetime.utcnow()
        nchandle.setncattr('History', global_atts['History'] +\
            '\n'+ '{histtime:%B %d, %Y %H:%M} UTC - {history}'.format(
                        histtime=histtime,
                        history=addhist))


    nchandle.close()


