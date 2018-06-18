"""
 Background:
 --------
 Nut_ncgen.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for bottle (nutrient) data
 Todo: switch from EPIC to CF

 File Format:
 ------------
 - E.Wisegarver nutrient csv output

 - combined seabird btl report output


 must specify the units (micromoles/kg or micromoles/l)

 History:
 --------
 2018-06-14: Bell - refactor starting with old NCnut_create.py routines

 Compatibility:
 --------------
 python >=3.6 - ?
 python 2.7 - ?

"""

#System Stack
import datetime
import argparse
import sys

#Science Stack
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2018, 7, 14)
__modified__ = datetime.datetime(2018, 7, 14)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet'

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Merge and archive nutrient csv data and bottle data')
parser.add_argument('CruiseID', 
	metavar='CruiseID', 
	type=str, 
	help='provide the cruiseid')
parser.add_argument('btlpath', 
	metavar='btlpath', 
	type=str, 
	help='full path to .btl_report')
parser.add_argument('nutpath', 
	metavar='nutpath', 
	type=int, 
	help='full path to nutrient csv file')
parser.add_argument('output', 
	metavar='output', 
	type=str, 
	help='full path to output folder (files will be generated there')
parser.add_argument('config_file_name', 
    metavar='config_file_name', 
    type=str, 
    help='full path to config file - eof_config.yaml')

args = parser.parse_args()

ndf = pd.read_csv(args.nutpath)

print("Nutrient Header Summary:")
print(ndf.info())

ndf.sort_values(['Cast','Niskin'],inplace=True)

reportdf = pd.read_csv(args.btlpath,delimiter='\s+')

print("Btl Report Header Summary:")
print(reportdf.info())

reportdf.sort_values(['cast','nb'],inplace=True)
#strip ctd from cast name and make integer
try:
	reportdf['CastNum'] = [int(x.lower().split('ctd')[-1]) for y,x in reportdf.cast.iteritems()]
except ValueError:
	sys.exit("Exiting: Report file doesn't have casts named as expected... ctdxxx")

#make a cast_niskin column to index on
print("Matching on Cast/Niskin pair.")
ndf['Cast_Niskin'] = [str(x['Cast']).zfill(3) + '_' + str(x['Niskin']).zfill(2) for y,x in ndf.iterrows()]
reportdf['Cast_Niskin'] = [str(x['CastNum']).zfill(3) + '_' + str(x['nb']).zfill(2) for y,x in reportdf.iterrows()]

###three potential merged results
# Matching Btl and Nut file
# No Btl - yes nut (no ctd information for this nut value...)
# Yes Btl - no nut 
temp = pd.merge(ndf, reportdf, on='Cast_Niskin', how='outer')
temp.sort_values(['Cast_Niskin'],inplace=True)

# Groupby Cast and write to file
# print out to screen data not saved due to lack of cast info (CTD)
# missing data is automatically excluded (NA groups)
gb =temp.groupby('cast')
