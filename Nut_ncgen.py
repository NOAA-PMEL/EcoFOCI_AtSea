"""
 Background:
 ===========
 Nut_ncgen.py
 
 
 Purpose:
 ========
 Creates EPIC flavored .nc files for bottle (nutrient) data
 Todo: switch from EPIC to CF

 File Format:
 ============
 - E.Wisegarver - nutrient csv output
 - S.Bell - combined seabird btl report output
 - Pavlof DB for cruise/cast metadata

 (Very Long) Example Usage:
 ==========================

 'python Nut_ncgen.pyDY1707 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/dy1707l1.report_btl 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/DiscreteNutrients/DY1707\ Nutrient\ Data.csv 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/ /Users/bell/Programs/Python/EcoFOCI_AtSea/config_files/nut_uml_epickeys.yaml'

 History:
 ========
 2018-06-14: Bell - refactor starting with old NCnut_create.py routines

 Compatibility:
 ==============
 python >=3.6 
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
import io_utils.EcoFOCI_netCDF_write as EcF_write


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
    type=str, 
    help='full path to nutrient csv file')
parser.add_argument('output', 
    metavar='output', 
    type=str, 
    help='full path to output folder (files will be generated there')
parser.add_argument('config_file_name', 
    metavar='config_file_name', 
    type=str, 
    help='full path to config file - nut_config.yaml')

args = parser.parse_args()

### Read Nutrient file - processed by E. Weisgarver and
# Bottle Report file obtained by concatenating bottle files without headers
ndf = pd.read_csv(args.nutpath)

print("Nutrient Header Summary:")
print(ndf.info())

reportdf = pd.read_csv(args.btlpath,delimiter='\s+',parse_dates=[['date','time']])

print("Btl Report Header Summary:")
print(reportdf.info())

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

# get config file for output content
if args.config_file_name.split('.')[-1] in ['json','pyini']:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name,'json')
elif args.config_file_name.split('.')[-1] in ['yaml']:
    EPIC_VARS_dict = ConfigParserLocal.get_config(args.config_file_name,'yaml')
else:
    sys.exit("Exiting: config files must have .pyini, .json, or .yaml endings")


for i,cast in enumerate(gb.groups):
    tdata=gb.get_group(cast).sort_values('CastNum')
    
    data_dic={}
    #prep dictionary to send to netcdf gen
    data_dic.update({'time':tdata['date_time'].values})
    data_dic.update({'dep':tdata['PrDM'].values})
    data_dic.update({'NH4_189':tdata['NH4 (uM)'].values})
    data_dic.update({'NO3_182':tdata['NO3 (uM)'].values})
    data_dic.update({'SI_188':tdata['Sil (uM)'].values})
    data_dic.update({'PO4_186':tdata['PO4 (uM)'].values})
    data_dic.update({'NO2_184':tdata['NO2 (uM)'].values})
    data_dic.update({'BTL_103':tdata['nb'].values})

    cruise = args.CruiseID.lower()
    cast = list(tdata.groupby('cast').groups.keys())[0]
    profile_name = args.output + cruise +\
                   cast.replace('ctd','c') +\
                   '_nut.nc' 
    
    history = 'File created by merging nutrient analysis and bottle report files'
    #build netcdf file - filename is castid
    ### Time should be consistent in all files as a datetime object
    #convert timestamp to datetime to epic time
    data_dic['time'] =  pd.to_datetime(data_dic['time'], format='%Y%m%d %H:%M:%S')
    time_datetime = [x.to_pydatetime() for x in data_dic['time']]
    time1,time2 = np.array(Datetime2EPIC(time_datetime), dtype='f8')

    ncinstance = EcF_write.NetCDF_Create_Profile(savefile=profile_name)
    ncinstance.file_create()
    ncinstance.sbeglobal_atts(raw_data_file=args.nutpath.split('/')[-1],
                                CruiseID=cruise,
                                Cast=cast)
    ncinstance.dimension_init(depth_len=len(tdata))
    ncinstance.variable_init(EPIC_VARS_dict)
    ncinstance.add_coord_data(depth=data_dic['dep'], 
                                latitude=1e35, 
                                longitude=1e35, 
                                time1=time1[0], time2=time2[0])
    ncinstance.add_data(EPIC_VARS_dict,data_dic=data_dic)
    ncinstance.add_history(history)
    ncinstance.close()

