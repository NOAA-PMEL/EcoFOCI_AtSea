#!/usr/bin/env python

"""

 Background:
 --------
 CTD_XSection_plot.py
 
 Purpose:
 --------
 Various routines for visualizing ALAMO data

 History:
 --------

"""

#System Stack
import datetime
import argparse

import numpy as np
import pandas as pd

# Visual Stack
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.dates import YearLocator, WeekdayLocator, MonthLocator, DayLocator, HourLocator, DateFormatter
import matplotlib.ticker as ticker
import cmocean

# Relative User Stack
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
from calc.EPIC2Datetime import EPIC2Datetime, get_UDUNITS
from calc.haversine import distance
from io_utils import ConfigParserLocal
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 9, 22)
__modified__ = datetime.datetime(2016, 9, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'ctd','FOCI'

mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.linewidth'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 2
mpl.rcParams['xtick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.major.size'] = 2
mpl.rcParams['ytick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'grey'
mpl.rcParams['xtick.color'] = 'grey'
# Example of making your own norm.  Also see matplotlib.colors.
# From Joe Kington: This one gives two different linear ramps:

class MidpointNormalize(colors.Normalize):
	def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
		self.midpoint = midpoint
		colors.Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip=None):
		# I'm ignoring masked values and all kinds of edge cases to make a
		# simple example...
		x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
		return np.ma.masked_array(np.interp(value, x, y))

"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='CTD X-section Contour plotter ')
parser.add_argument('PointerFile', metavar='PointerFile', type=str,
			   help='full path to confige PointerFile file')
parser.add_argument("-dx",'--delta_x', 
	action="store_true", 
	help='plot x-axis as distance instead of time')
args = parser.parse_args()

"""---------------------------------------------------------------------------------------
Get parameters from specified pointerfile - 
an example is shown in the header description of
this program.  It can be of the .pyini (json) form or .yaml form

"""
if args.PointerFile.split('.')[-1] == 'pyini':
	pointer_file = ConfigParserLocal.get_config(args.PointerFile)
elif args.PointerFile.split('.')[-1] == 'yaml':
	pointer_file = ConfigParserLocal.get_config_yaml(args.PointerFile)
else:
	print "PointerFile format not recognized"
	sys.exit()


CTDDataPath = pointer_file['ctd_data_path']
ctd_files = pointer_file['ctd_files']
ctd_files_path = [CTDDataPath+b for b in ctd_files]

depth_array = np.arange(0,pointer_file['maxdepth_m']+1,pointer_file['depth_interval_m']) 
temparray = np.ones((len(ctd_files_path),len(depth_array)))*np.nan
ProfileTime = []

fig = plt.figure(1, figsize=(12, 3), facecolor='w', edgecolor='w')
ax1 = fig.add_subplot(111)		
for castnum, cast in enumerate(sorted(ctd_files_path)):

	#open/read netcdf files
	print "Reading {cast}".format(cast=cast)
	df = EcoFOCI_netCDF(cast)
	global_atts = df.get_global_atts()
	vars_dic = df.get_vars()
	ncdata = df.ncreadfile_dic()
	df.close()
	nctime = get_UDUNITS(EPIC2Datetime(ncdata['time'],ncdata['time2']),'days since 0001-01-01') + 1.

	try:
		if castnum == 0:
			ProfileDist = [0.0]
			last_coord = [ncdata['lat'][0],ncdata['lon'][0]]
		else:
			ProfileDist = ProfileDist + [distance(last_coord,[ncdata['lat'][0],ncdata['lon'][0]])]
		ProfileTime = ProfileTime + [nctime[0]]
		Pressure = ncdata['dep'][:]
		tempvar = ncdata[pointer_file['EPIC_Key']][0,:,0,0]
		tempvar[np.where(tempvar >1e30)[0]] = np.nan

		temparray[castnum,:] = np.interp(depth_array,Pressure,tempvar,left=np.nan,right=np.nan)

		xtime = np.ones_like(np.array(Pressure)) * (nctime[0])
		xdist = np.ones_like(np.array(Pressure)) * (distance(last_coord,[ncdata['lat'][0],ncdata['lon'][0]]))
		#turn off below and set zorder to 1 for no scatter plot colored by points
		if not args.delta_x:
			plt.scatter(x=xtime, y=Pressure,s=1,marker='.', edgecolors='none', c='k', zorder=3, alpha=0.3) 
			plt.scatter(x=xtime, y=Pressure,s=15,marker='.', edgecolors='none', c=tempvar, 
			vmin=pointer_file['rangemin'], vmax=pointer_file['rangemax'], 
			cmap=cmocean.cm.cmap_d[pointer_file['colormap_name']], zorder=1)
		else:
			plt.scatter(x=xdist, y=Pressure,s=1,marker='.', edgecolors='none', c='k', zorder=3, alpha=0.3) 
			plt.scatter(x=xdist, y=Pressure,s=15,marker='.', edgecolors='none', c=tempvar, 
			vmin=pointer_file['rangemin'], vmax=pointer_file['rangemax'], 
			cmap=cmocean.cm.cmap_d[pointer_file['colormap_name']], zorder=1)
	except IndexError:
		pass

if not args.delta_x:
	cbar = plt.colorbar()
	cbar.set_label(pointer_file['Clabel'],rotation=0, labelpad=90)
	plt.contourf(ProfileTime,depth_array,temparray.T, 
		extend='both', cmap=cmocean.cm.cmap_d[pointer_file['colormap_name']], levels=np.arange(pointer_file['rangemin'],pointer_file['rangemax'],0.25), alpha=0.75)

	ax1.invert_yaxis()
	ax1.xaxis.set_major_locator(DayLocator(bymonthday=15))
	ax1.xaxis.set_minor_locator(DayLocator(bymonthday=[5,10,15,20,25,30]))
	ax1.xaxis.set_major_formatter(ticker.NullFormatter())
	ax1.xaxis.set_minor_formatter(DateFormatter('%d'))
	ax1.xaxis.set_major_formatter(DateFormatter('%b %y'))
	ax1.xaxis.set_tick_params(which='major', pad=15)

	plt.tight_layout()
	plt.savefig('images/' + pointer_file['CruiseID'] + '_' + pointer_file['EPIC_Key'] + '.png', transparent=False, dpi = (300))
	plt.close()
else:
	cbar = plt.colorbar()
	cbar.set_label(pointer_file['Clabel'],rotation=0, labelpad=90)
	plt.contourf(ProfileDist,depth_array,temparray.T, 
		extend='both', cmap=cmocean.cm.cmap_d[pointer_file['colormap_name']], levels=np.arange(pointer_file['rangemin'],pointer_file['rangemax'],0.25), alpha=0.75)

	ax1.invert_yaxis()
	plt.tight_layout()
	plt.savefig('images/' + pointer_file['CruiseID'] + '_' + pointer_file['EPIC_Key'] + '.png', transparent=False, dpi = (300))
	plt.close()