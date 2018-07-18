#!/usr/bin/env python

"""
ctd_TvS.py

TS plot

Input - CruiseID

Options - temperature and salinity bounds
Options - individual profiles or entire cruises

 History:
 ========
 2018-07-13: Make python3 compliant
 2018-03-27: Modify so that an entire cruise can be plotted on one plot with
    options for colorcoding data.
 2017-06-21: Migrate to EcoFOCI_MooringAnalysis pkg and unify netcdf creation
    code so that it is no longer instrument dependant


 Compatibility:
 ==============
 python >=3.6 
 python 2.7 

"""

from __future__ import (absolute_import, division, print_function)

#System Stack
import datetime
import os
import argparse

#Science Stack
import numpy as np
from netCDF4 import Dataset
import seawater as sw

#Visual Packages
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# User Stack
from utilities import ncutilities as ncutil

# Relative User Stack
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
from calc.EPIC2Datetime import EPIC2Datetime, get_UDUNITS
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2014, 6, 24)
__version__  = "0.3.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Plots', 'Cruise', 'QC'

"""--------------------------------Plot Routines---------------------------------------"""


def plot_salvtemp(salt, temp, press, srange=[0,1], trange=[0,10], ptitle=""): 
    plt.style.use('ggplot')
    
    # Figure out boudaries (mins and maxs)
    smin = srange[0]
    smax = srange[1]
    tmin = trange[0]
    tmax = trange[1]

    # Calculate how many gridcells we need in the x and y dimensions
    xdim = int(round((smax-smin)/0.1+1,0))
    ydim = int(round((tmax-tmin)+1,0))
    
    #print 'ydim: ' + str(ydim) + ' xdim: ' + str(xdim) + ' \n'
    if (xdim > 10000) or (ydim > 10000): 
        print('To many dimensions for grid in {0} {1} file. Likely  missing data \n'.format(cruise,cast))
        return
 
    # Create empty grid of zeros
    dens = np.zeros((ydim,xdim))
 
    # Create temp and salt vectors of appropiate dimensions
    ti = np.linspace(0,ydim-1,ydim)+tmin
    si = np.linspace(0,xdim-1,xdim)*0.1+smin
 
    # Loop to fill in grid with densities
    for j in range(0,int(ydim)):
        for i in range(0, int(xdim)):
            dens[j,i]=sw.dens0(si[i],ti[j])
 
    # Substract 1000 to convert to sigma-t
    dens = dens - 1000
 
    # Plot data ***********************************************
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    CS = plt.contour(si,ti,dens, linestyles='dashed', colors='k')
    plt.clabel(CS, fontsize=12, inline=1, fmt='%1.1f') # Label every second level
 
    ts = ax1.scatter(salt,temp, c=press, cmap='gray', s=100)
    plt.colorbar(ts )
    plt.ylim(tmin,tmax)
    plt.xlim(smin,smax)
 
    ax1.set_xlabel('Salinity (PSU)')
    ax1.set_ylabel('Temperature (C)')

    
    t = fig.suptitle(ptitle, fontsize=12, fontweight='bold')
    t.set_y(1.08)
    return fig    



"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='CTD T/S Property/Property plot')
parser.add_argument('DataPath', 
        metavar='DataPath', 
        type=str,
        help='full path to directory of processed nc files. \
        This plots each file individually unless -fc flag is passed')
parser.add_argument('-fc', '--full_cruise', 
        action="store_true",
        help='Use all cruise casts')
parser.add_argument('-ss','--sal_scale', 
        nargs='+',
        type=float,
        help='fixed salinity scale (min max)')
parser.add_argument('-ts','--temp_scale', 
        nargs='+', 
        type=float, 
        help='fixed temperature scale (min max)')

args = parser.parse_args()

nc_path = args.DataPath

if not '.nc' in nc_path:
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]
else:
    nc_path = [nc_path,]

    
# Break the routines into two identical structures in which one ingests all the data
#  and the other plots cast by cast.
#  Its poor coding so fix later 
if args.full_cruise:


    for ncfile in sorted(nc_path):

        print("Working on file {} ".format(ncfile))

        nc = EcoFOCI_netCDF(ncfile)
        ncdata = nc.ncreadfile_dic()
        g_atts = nc.get_global_atts()
        nc.close()

        try:
            ncdata['S_41']
        except:
            continue

        if not os.path.exists('images/' + g_atts['CRUISE']):
            os.makedirs('images/' + g_atts['CRUISE'])
        if not os.path.exists('images/' + g_atts['CRUISE'] + '/TS_plot/'):
            os.makedirs('images/' + g_atts['CRUISE'] + '/TS_plot/')


        cast_time = EPIC2Datetime(ncdata['time'],ncdata['time2'])[0]
        all_temperature = all_salinity = all_depth = all_times = [] 
        all_times = all_times + [cast_time]
        all_temperature = all_temperature + [ncdata['T_28'][0,:,0,0]]
        all_salinity = all_salinity + [ncdata['S_41'][0,:,0,0]]
        all_depth = all_depth + [ncdata['dep']]


    ptitle = ("Plotted on: {0} from {1} \n\n"
              "Cruise: {2} Cast: {3}  Stn: {4} \n"
              "Lat: {5:3.3f}  Lon: {6:3.3f} at {7}\n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                              'All', g_atts['CRUISE'], 'All', g_atts['STATION_NAME'], 
                                              ncdata['lat'][0], ncdata['lon'][0], datetime.datetime.strftime(cast_time,"%Y-%m-%d %H:%M GMT" ))

    all_salinity = np.array(all_salinity)
    all_temperature = np.array(all_temperature)
    all_depth = np.array(all_depth)

    if args.sal_scale and args.temp_scale:
        fig = plot_salvtemp(all_salinity, all_temperature, all_depth,\
                            args.sal_scale, args.temp_scale, ptitle)
    else:
        # Figure out boudaries (mins and maxs)
        smin = all_salinity.min() - (0.01 * all_salinity.min())
        smax = all_salinity.max() + (0.01 * all_salinity.max())
        tmin = all_temperature.min() - (0.1 * all_temperature.max())
        tmax = all_temperature.max() + (0.1 * all_temperature.max())
        fig = plot_salvtemp(all_salinity, all_temperature, all_depth,\
                            [smin, smax], [tmin, tmax], ptitle)

    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0], DefaultSize[1]) )
    plt.savefig('images/' + g_atts['CRUISE'] + '/TS_plot/' + g_atts['CRUISE'] + '_TSplot.png', bbox_inches='tight', dpi = (300))
    plt.close()

else:
    #Individual plots per file/cast  
    for ncfile in sorted(nc_path):
     
        print("Working on file {} ".format(ncfile))

        nc = EcoFOCI_netCDF(ncfile)
        ncdata = nc.ncreadfile_dic()
        g_atts = nc.get_global_atts()
        nc.close()

        if not os.path.exists('images/' + g_atts['CRUISE']):
            os.makedirs('images/' + g_atts['CRUISE'])
        if not os.path.exists('images/' + g_atts['CRUISE'] + '/TS_plot/'):
            os.makedirs('images/' + g_atts['CRUISE'] + '/TS_plot/')

        try:
            ncdata['S_41']
        except:
            continue

        cast_time = EPIC2Datetime(ncdata['time'],ncdata['time2'])[0]
            
        ptitle = ("Plotted on: {0} from {1} \n\n"
                  "Cruise: {2} Cast: {3}  Stn: {4} \n"
                  "Lat: {5:3.3f}  Lon: {6:3.3f} at {7}\n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                                  ncfile.split('/')[-1], g_atts['CRUISE'], g_atts['CAST'], g_atts['STATION_NAME'], 
                                                  ncdata['lat'][0], ncdata['lon'][0], datetime.datetime.strftime(cast_time,"%Y-%m-%d %H:%M GMT" ))



        if args.sal_scale and args.temp_scale:
            fig = plot_salvtemp(ncdata['S_41'][0,:,0,0], ncdata['T_28'][0,:,0,0], ncdata['dep'],\
                                args.sal_scale, args.temp_scale, ptitle)
        else:
            # Figure out boudaries (mins and maxs)
            smin = ncdata['S_41'][0,:,0,0].min() - (0.01 * ncdata['S_41'][0,:,0,0].min())
            smax = ncdata['S_41'][0,:,0,0].max() + (0.01 * ncdata['S_41'][0,:,0,0].max())
            tmin = ncdata['T_28'][0,:,0,0].min() - (0.1 * ncdata['T_28'][0,:,0,0].max())
            tmax = ncdata['T_28'][0,:,0,0].max() + (0.1 * ncdata['T_28'][0,:,0,0].max())
            fig = plot_salvtemp(ncdata['S_41'][0,:,0,0], ncdata['T_28'][0,:,0,0], ncdata['dep'],\
                                [smin, smax], [tmin, tmax], ptitle)

        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]) )
        plt.savefig('images/' + g_atts['CRUISE'] + '/TS_plot/' + ncfile.split('/')[-1].split('.')[0] + '_TSplot.png', bbox_inches='tight', dpi = (300))
        plt.close()


    

