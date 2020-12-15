#!/usr/bin/env

"""
CTDvPrawler_plot.py

Plot data from cruises

Currently
---------
ctd plots
plots prawler data as secondary

Input - CruiseID


 Compatibility:
 ==============
 python >=3.6 
 python 2.7 

"""
from __future__ import absolute_import, division, print_function

import argparse
import datetime
import os

import matplotlib as mpl
import numpy as np
from netCDF4 import Dataset

mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

from plots.profile_plot import CTDProfilePlot

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
from calc.EPIC2Datetime import EPIC2Datetime, get_UDUNITS
from calc.haversine import distance
from io_utils import ConfigParserLocal
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 8, 22)
__modified__ = datetime.datetime(2016, 8, 24)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Plots', 'Cruise', 'QC'



"""--------------------------------Plot Routines---------------------------------------"""

def twovar_minmax_plotbounds(var1,var2):
    """expects missing values to be np.nan"""
    if np.isnan(var1).all() and np.isnan(var2).all():
        min_bound = -1
        max_bound = 1
    elif np.isnan(var1).all() and not np.isnan(var2).all():
        min_bound = var2[~np.isnan(var2)].min()
        max_bound = var2[~np.isnan(var2)].max()
    elif np.isnan(var2).all() and not np.isnan(var1).all():
        min_bound = var1[~np.isnan(var1)].min()
        max_bound = var1[~np.isnan(var1)].max()
    else:
        min_bound = np.min((var1[~np.isnan(var1)].min(), var2[~np.isnan(var2)].min()))
        max_bound = np.max((var1[~np.isnan(var1)].max(), var2[~np.isnan(var2)].max()))
        
    return (min_bound, max_bound)
   

"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,help='full path to directory of processed nc files')
parser.add_argument('PrawlerDataPath', metavar='PrawlerDataPath', type=str,help='full path to directory of processed prawler nc files')
parser.add_argument('PrawlerProfileID', metavar='PrawlerProfileID', type=int,help='sequential prawler profile id')
parser.add_argument('-TSvD','--TSvD', action="store_true",
               help='Temperature, Salinity, SigmaT vs depth')
parser.add_argument('-OxyFluor','--OxyFluor', action="store_true",
               help='Temperature, Oxygen, Fluorometer vs depth')
parser.add_argument('-OxyConcFluor','--OxyConcFluor', action="store_true",
               help='Temperature, Oxygen Concentration, Fluorometer vs depth')
parser.add_argument('-ParTurbFluor','--ParTurbFluor', action="store_true",
               help='PAR, Turbidity, Fluorometer vs depth')
parser.add_argument('-ParFluor','--ParFluor', action="store_true",
               help='PAR, Fluorometer vs depth')
parser.add_argument('-TurbFluor','--TurbFluor', action="store_true",
               help='Turbidity, Fluorometer vs depth (common for only Eco')
parser.add_argument('-ParTransFluor','--ParTransFluor', action="store_true",
               help='Transmissometer, Turbidity, Fluorometer vs depth (common package for EMA)')
parser.add_argument('-TransTurbFluor','--TransTurbFluor', action="store_true",
               help='Transmissometer, Turbidity, Fluorometer vs depth (common package for EMA)')
parser.add_argument('-TransFluor','--TransFluor', action="store_true",
               help='Transmissometer, Fluorometer vs depth (common package for EMA)')

args = parser.parse_args()

ncfile=args.DataPath
print("Working on file {file} ").format(file=ncfile)
nc = EcoFOCI_netCDF(ncfile)
ncdata = nc.ncreadfile_dic()
g_atts = nc.get_global_atts()
nc.close()
cast_time = EPIC2Datetime(ncdata['time'],ncdata['time2'])[0]

ncfilep=args.PrawlerDataPath
print("Working on file {file} ").format(file=ncfilep)
nc = EcoFOCI_netCDF(ncfilep)
ncdatap = nc.ncreadfile_dic()
g_attsp = nc.get_global_atts()
nc.close()



if np.ndim(ncdata['dep']) == 1:
    ydata = ncdata['dep'][:]
else:
    ydata = ncdata['dep'][0,:,0,0]

for dkey in ncdata.keys():
    if not dkey in ['lat','lon','depth','dep','time','time2']:
        ncdata[dkey][0,ncdata[dkey][0,:,0,0] >= 1e30,0,0] = np.nan

for dkey in ncdatap.keys():
    ncdatap[dkey][ncdatap[dkey] >= 1e30] = np.nan

if not os.path.exists('images/' + g_atts['CRUISE']):
    os.makedirs('images/' + g_atts['CRUISE'])
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TSSigma/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TSSigma/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TO2F/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TO2F/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TO2concF/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TO2concF/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/PARTurbFluor/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/PARTurbFluor/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TurbFluor/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TurbFluor/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/ParTransFluor/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/ParTransFluor/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TransTurbFluor/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TransTurbFluor/')
if not os.path.exists('images/' + g_atts['CRUISE'] + '/TransFluor/'):
    os.makedirs('images/' + g_atts['CRUISE'] + '/TransFluor/')

try:
    g_atts['STATION_NAME'] = g_atts['STATION_NAME']
except:
    g_atts['STATION_NAME'] = 'NA'

if args.TSvD:
    CTDplot = CTDProfilePlot()

    (plt, fig) = CTDplot.plot3var2y(epic_key=['T_28','T2_35','S_41','S_42','ST_70','ST_2070'],
                     xdata=[ncdata['T_28'][0,:,0,0],ncdatap['Temperature'][args.PrawlerProfileID],
                            ncdata['S_41'][0,:,0,0],ncdatap['Salinity'][args.PrawlerProfileID],
                            ncdata['ST_70'][0,:,0,0],ncdatap['SigmaT'][args.PrawlerProfileID]],
                     ydata=ydata,
                     ydata2=ncdatap['Depth'][args.PrawlerProfileID],
                     xlabel=['Temperature (C)','Salinity (PSU)','SigmaT (kg/m^3)'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TSSigma/' + ncfile.split('/')[-1].split('.')[0] + '_plot_2TSSigma.png', bbox_inches='tight', dpi = (300))
    plt.close()


if args.OxyFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var2y(epic_key=['T_28','T2_35','OST_62','CTDOST_4220',fluor_key,'Prawler_Fluor'],
                     xdata=[ncdata['T_28'][0,:,0,0],ncdatap['Temperature'][args.PrawlerProfileID],
                            ncdata['OST_62'][0,:,0,0],ncdatap['Oxy_Sat'][args.PrawlerProfileID],
                            ncdata[fluor_key][0,:,0,0],ncdatap['Chlorophyll'][args.PrawlerProfileID]],
                     ydata=ydata,
                     ydata2=ncdatap['Depth'][args.PrawlerProfileID],                     
                     xlabel=['Temperature (C)','Oxygen % Sat.','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TO2F/' + ncfile.split('/')[-1].split('.')[0] + '_plot_TO2F.png', bbox_inches='tight', dpi = (300))
    plt.close()


if args.OxyFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var2y(epic_key=['T_28','T2_35','O_65','CTDOXY_4221',fluor_key,'Prawler_Fluor'],
                     xdata=[ncdata['T_28'][0,:,0,0],ncdatap['Temperature'][args.PrawlerProfileID],
                            ncdata['O_65'][0,:,0,0],ncdatap['Oxy_Conc'][args.PrawlerProfileID],
                            ncdata[fluor_key][0,:,0,0],ncdatap['Chlorophyll'][args.PrawlerProfileID]],
                     ydata=ydata,
                     ydata2=ncdatap['Depth'][args.PrawlerProfileID],                     
                     xlabel=['Temperature (C)','Oxygen Conc.','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TO2concF/' + ncfile.split('/')[-1].split('.')[0] + '_plot_TO2concF.png', bbox_inches='tight', dpi = (300))
    plt.close()


if args.ParFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot2var(epic_key=['PAR_905','',fluor_key,''],
                     xdata=[ncdata['PAR_905'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['PAR','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/PARFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_PARFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.TurbFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot2var(epic_key=['Trb_980','',fluor_key,''],
                     xdata=[ncdata['Trb_980'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['Turbidity','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TurbFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_TurbFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.ParTurbFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var(epic_key=['PAR_905','','Trb_980','',fluor_key,''],
                     xdata=[ncdata['PAR_905'][0,:,0,0],np.array([]),
                            ncdata['Trb_980'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['PAR','Turbidity','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/PARTurbFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_PARTurbFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.ParTransFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var(epic_key=['PAR_905','','Tr_904','',fluor_key,''],
                     xdata=[ncdata['PAR_905'][0,:,0,0],np.array([]),
                            ncdata['Tr_904'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['PAR','Trans. %','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/ParTransFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_PARTransFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.ParTurbFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var(epic_key=['PAR_905','','Trb_980','',fluor_key,''],
                     xdata=[ncdata['PAR_905'][0,:,0,0],np.array([]),
                            ncdata['Trb_980'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['PAR','Turbidity','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/PARTurbFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_PARTurbFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.TransTurbFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot3var(epic_key=['Tr_904','','Trb_980','',fluor_key,''],
                     xdata=[ncdata['Tr_904'][0,:,0,0],np.array([]),
                            ncdata['Trb_980'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['Trans. %','Turbidity','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TransTurbFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_TransTurbFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()

if args.TransFluor:
    CTDplot = CTDProfilePlot()

    fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
    for fkey in fluor_key_list:
        if fkey in ncdata.keys():
            fluor_key = fkey

    (plt, fig) = CTDplot.plot2var(epic_key=['Tr_904','',fluor_key,''],
                     xdata=[ncdata['Tr_904'][0,:,0,0],np.array([]),
                            ncdata[fluor_key][0,:,0,0],np.array([])],
                     ydata=ydata,
                     xlabel=['Trans. %','Chlor-A mg/m^3'],
                     secondary=True)

    ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                      fileid=ncfile.split('/')[-1],
                      castid=g_atts['CAST'],
                      stationid=g_atts['STATION_NAME'],
                      castdate=cast_time,
                      lat=ncdata['lat'][0],
                      lon=ncdata['lon'][0])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

    plt.savefig('images/' + g_atts['CRUISE'] + '/TransFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_TransFluor.png', bbox_inches='tight', dpi = (300))
    plt.close()        
