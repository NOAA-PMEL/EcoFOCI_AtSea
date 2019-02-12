#!/usr/bin/env python

"""
Background:
===========
StripEPICvars_cmdline.py

Removes some variables from .nc files that are not recognized by EPIC edit_look routine
via the shell netcdf utilities

StripEPICvars_cmdline.py /Users/bell/Data_Local/FOCI/ecoraid/2014/CTDCasts/ae1401/ --EPIC_Keys time time2 dep lat lon T_28 \
    T2_35 S_41 S_42 ST_70 OST_62 O_65 Trb_980 PAR_905 CTDOXY_4221 CTDOST_4220 F_903 

Input - CruiseID

History:
=======

2019-02-12: Migrate to python3

Compatibility:
==============
python >=3.6 - Not Tested
python 2.7 

"""

#System Stack
import datetime
import shutil
import os
import argparse


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2019, 2, 12)
__version__  = "0.1.1"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

    
"""------------------------------------- System ---------------------------------------"""

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)    
    
"""------------------------------------- EPIC Strip -----------------------------------"""

def StripEPIC(user_in, user_out, keep_vars):

    cruiseID = user_in.split('/')[-2]
    leg = cruiseID.lower().split('L')
    if len(leg) == 1:
        cruiseID = leg[0]
        leg = ''
    else:
        cruiseID = leg[0] + 'L' + leg[-1]

    keep_vars = keep_vars
    
    #epic flavored nc files
    nc_path = user_out
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc')]

    print(user_in, user_out)
    nocopy_flag = 0
    if os.path.exists("/".join(nc_path[0].split('/')[:-1])+'/allparameters/'):
        print("Originals have already been copied... not adding current dir to orig directory")
        nocopy_flag = 1
    
    createDir("/".join(nc_path[0].split('/')[:-1])+'/allparameters/')

    for ncfile in nc_path:
        print("Working on {ncfile}".format(ncfile=ncfile))
        if nocopy_flag == 0:
            shutil.copy (ncfile, "/".join(ncfile.split('/')[:-1])+'/allparameters/'+ncfile.split('/')[-1])

        os.system("nccopy -V "+ ",".join(keep_vars) + " " + "/".join(ncfile.split('/')[:-1])+'/allparameters/'+ncfile.split('/')[-1] + " " + ncfile)
    
    processing_complete = True
    return processing_complete
"""------------------------------------- Main Routine -----------------------------------------"""

parser = argparse.ArgumentParser(description='Maintain only specified EPIC keys')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .nc file')
parser.add_argument('--EPIC_Keys', nargs='+', type=str, help='EPIC Keys to keep seperated by spaces')

args = parser.parse_args()


user_in = args.inputpath
user_out = user_in
EPIC_Keys = args.EPIC_Keys

StripEPIC(user_in, user_out, EPIC_Keys)