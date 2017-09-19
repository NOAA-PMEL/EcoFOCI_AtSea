#!/usr/bin/env

"""
class definitions for ctd profile plots

limit to four variables

"""

#System Stack
import datetime

# science stack
import numpy as np

# Visual Stack

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, WeekdayLocator, MonthLocator, DayLocator, HourLocator, DateFormatter
import matplotlib.ticker as ticker


class CTDProfilePlot(object):


    def __init__(self, fontsize=10, labelsize=10, plotstyle='k-.', stylesheet='seaborn-ticks'):
        """Initialize the timeseries with items that do not change.

        This sets up the axes and station locations. The `fontsize` and `spacing`
        are also specified here to ensure that they are consistent between individual
        station elements.

        Parameters
        ----------
        fontsize : int
            The fontsize to use for drawing text
        labelsize : int
          The fontsize to use for labels
        stylesheet : str
          Choose a mpl stylesheet [u'seaborn-darkgrid', 
          u'seaborn-notebook', u'classic', u'seaborn-ticks', 
          u'grayscale', u'bmh', u'seaborn-talk', u'dark_background', 
          u'ggplot', u'fivethirtyeight', u'seaborn-colorblind', 
          u'seaborn-deep', u'seaborn-whitegrid', u'seaborn-bright', 
          u'seaborn-poster', u'seaborn-muted', u'seaborn-paper', 
          u'seaborn-white', u'seaborn-pastel', u'seaborn-dark', 
          u'seaborn-dark-palette']
        """

        self.fontsize = fontsize
        self.labelsize = labelsize
        self.plotstyle = plotstyle
        self.max_xticks = 10
        plt.style.use(stylesheet)
        mpl.rcParams['svg.fonttype'] = 'none'
        mpl.rcParams['axes.grid'] = True
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


    @staticmethod
    def add_title(cruiseid='', fileid='', stationid='',castid='',castdate=datetime.datetime.now(),lat=-99.9,lon=-99.9):
      """Pass parameters to annotate the title of the plot

      This sets the standard plot title using common meta information from PMEL/EPIC style netcdf files

      Parameters
      ----------
      cruiseid : str
        Cruise Identifier
      fileid : str
        File Identifier
      stationid : str
        Station Identifier
      lat : float
        The latitude of the mooring
      lon : float
        The longitude of the mooring
      """  

      ptitle = ("Plotted on: {time:%Y/%m/%d %H:%M} \n from {fileid} \n "
                "Cruise: {cruiseid}  Cast: {castid}  Stn: {stationid} \n"
                "Lat: {latitude:3.3f}  Lon: {longitude:3.3f} at {castdate}" 
    			  " ").format(
    			  time=datetime.datetime.now(), 
                  cruiseid=cruiseid,
                  stationid=stationid,
                  castid=castid,
                  fileid=fileid,
                  latitude=lat, 
                  longitude=lon, 
                  castdate=datetime.datetime.strftime(castdate,"%Y-%m-%d %H:%M GMT" ) )

      return ptitle

    def plot1var(self, epic_key=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
      fig = plt.figure(1)
      ax1 = fig.add_subplot(111)
      p1 = ax1.plot(xdata[0], ydata)
      plt.setp(p1, **(self.var2format(epic_key[0])))
      if secondary:
        p1 = ax1.plot(xdata[1],ydata)
        plt.setp(p1, **(self.var2format(epic_key[1])))

      ax1.invert_yaxis()
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel, fontsize=self.labelsize, fontweight='bold')

      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax1.xaxis.set_major_formatter(fmt)
      ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

      return plt, fig

    def plot2var(self, epic_key=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
      fig = plt.figure(1)
      ax1 = fig.add_subplot(111)
      p1 = ax1.plot(xdata[0], ydata)
      plt.setp(p1, **(self.var2format(epic_key[0])))
      if secondary:
        p1 = ax1.plot(xdata[1],ydata)
        plt.setp(p1, **(self.var2format(epic_key[1])))

      ax1.invert_yaxis()
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')

      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax1.xaxis.set_major_formatter(fmt)
      ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

      #plot second param
      ax2 = ax1.twiny()
      p1 = ax2.plot(xdata[2], ydata)
      plt.setp(p1, **(self.var2format(epic_key[2])))
      if secondary:
        p1 = ax2.plot(xdata[3],ydata)
        plt.setp(p1, **(self.var2format(epic_key[3])))

      plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
      plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

      #set xticks and labels to be at the same spot for all the vars
      ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
      ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))

      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax2.xaxis.set_major_formatter(fmt)
      ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)

      return plt, fig

    def plot3var(self, epic_key=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
      fig = plt.figure(1)
      ax1 = fig.add_subplot(111)
      p1 = ax1.plot(xdata[0], ydata)
      plt.setp(p1, **(self.var2format(epic_key[0])))
      if secondary and not (xdata[1].size == 0):
        p1 = ax1.plot(xdata[1],ydata)
        plt.setp(p1, **(self.var2format(epic_key[1])))
        #set plot limits for two vars by finding the absolute range and adding 10%
        abmin=np.min([np.nanmin(xdata[0]),np.nanmin(xdata[1])])
        abmax=np.max([np.nanmax(xdata[0]),np.nanmax(xdata[1])])
        ax1.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

      ax1.invert_yaxis()
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')
    
      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax1.xaxis.set_major_formatter(fmt)
      ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

      #plot second param
      ax2 = ax1.twiny()
      p1 = ax2.plot(xdata[2], ydata)
      plt.setp(p1, **(self.var2format(epic_key[2])))
      if secondary and not (xdata[3].size == 0):
        p1 = ax2.plot(xdata[3],ydata)
        plt.setp(p1, **(self.var2format(epic_key[3])))
        #set plot limits for two vars by finding the absolute range and adding 10%
        abmin=np.min([np.nanmin(xdata[2]),np.nanmin(xdata[3])])
        abmax=np.max([np.nanmax(xdata[2]),np.nanmax(xdata[3])])
        ax2.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax2.xaxis.set_major_formatter(fmt)
      ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)

      ax3 = ax1.twiny()
      ax3.spines["top"].set_position(("axes", 1.05))
      self.make_patch_spines_invisible(ax3)
      # Second, show the right spine.
      ax3.spines["top"].set_visible(True)
      p1 = ax3.plot(xdata[4], ydata)
      plt.setp(p1, **(self.var2format(epic_key[4])))
      if secondary and not (xdata[5].size == 0):
        p1 = ax2.plot(xdata[5],ydata)
        plt.setp(p1, **(self.var2format(epic_key[5])))
        #set plot limits for two vars by finding the absolute range and adding 10%
        abmin=np.min([np.nanmin(xdata[4]),np.nanmin(xdata[5])])
        abmax=np.max([np.nanmax(xdata[4]),np.nanmax(xdata[5])])
        ax3.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[2], fontsize=self.labelsize, fontweight='bold')

      #set bounds based on max and min values

      #set xticks and labels to be at the same spot for all three vars
      ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
      ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))
      ax3.set_xticks(np.linspace(ax3.get_xbound()[0], ax3.get_xbound()[1], self.max_xticks))

      fmt=mpl.ticker.FormatStrFormatter('%.3f')
      ax3.xaxis.set_major_formatter(fmt)
      ax3.tick_params(axis='x', which='major', labelsize=self.labelsize)

      return plt, fig

    def plot3var2y(self, epic_key=None, xdata=None, ydata=None, ydata2=None, xlabel=None, secondary=False, **kwargs):
      fig = plt.figure(1)
      ax1 = fig.add_subplot(111)
      p1 = ax1.plot(xdata[0], ydata)
      plt.setp(p1, **(self.var2format(epic_key[0])))
      if secondary and not (xdata[1].size == 0):
        p1 = ax1.plot(xdata[1],ydata2)
        plt.setp(p1, **(self.var2format(epic_key[1])))

      ax1.invert_yaxis()
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')
    
      fmt=mpl.ticker.ScalarFormatter(useOffset=False)
      fmt.set_scientific(False)
      ax1.xaxis.set_major_formatter(fmt)
      ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

      #plot second param
      ax2 = ax1.twiny()
      p1 = ax2.plot(xdata[2], ydata)
      plt.setp(p1, **(self.var2format(epic_key[2])))
      if secondary and not (xdata[3].size == 0):
        p1 = ax2.plot(xdata[3],ydata2)
        plt.setp(p1, **(self.var2format(epic_key[3])))

      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

      fmt=mpl.ticker.ScalarFormatter(useOffset=False)
      fmt.set_scientific(False)
      ax2.xaxis.set_major_formatter(fmt)
      ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)

      ax3 = ax1.twiny()
      ax3.spines["top"].set_position(("axes", 1.05))
      self.make_patch_spines_invisible(ax3)
      # Second, show the right spine.
      ax3.spines["top"].set_visible(True)
      p1 = ax3.plot(xdata[4], ydata)
      plt.setp(p1, **(self.var2format(epic_key[4])))
      if secondary and not (xdata[5].size == 0):
        p1 = ax3.plot(xdata[5],ydata2)
        plt.setp(p1, **(self.var2format(epic_key[5])))
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel(xlabel[2], fontsize=self.labelsize, fontweight='bold')

      #set xticks and labels to be at the same spot for all three vars
      ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
      ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))
      ax3.set_xticks(np.linspace(ax3.get_xbound()[0], ax3.get_xbound()[1], self.max_xticks))

      fmt=mpl.ticker.ScalarFormatter(useOffset=False)
      fmt.set_scientific(False)
      ax3.xaxis.set_major_formatter(fmt)
      ax3.tick_params(axis='x', which='major', labelsize=self.labelsize)

      return plt, fig


    @staticmethod
    def var2format(epic_key):
      """list of plot specifics based on variable name"""
      plotdic={}
      if epic_key in ['T_28']:
        plotdic['color']='red'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.5
      elif epic_key in ['T2_35']:
        plotdic['color']='magenta'
        plotdic['linestyle']='--'
        plotdic['linewidth']=0.5
      elif epic_key in ['S_41', 'OST_62', 'O_65']:
        plotdic['color']='blue'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.5
      elif epic_key in ['S_42', 'CTDOST_4220', 'CTDOXY_4221']:
        plotdic['color']='cyan'
        plotdic['linestyle']='--'
        plotdic['linewidth']=0.5
      elif epic_key in ['ST_70','Trb_980','SigmaT']:
        plotdic['color']='black'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.5
      elif epic_key in ['F_903','fWS_973','Fch_906']:
        plotdic['color']='green'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.5
      elif epic_key in ['PAR_905']:
        plotdic['color']='darkorange'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.75
      else:
        plotdic['color']='black'
        plotdic['linestyle']='--'
        plotdic['linewidth']=1.0      

      return plotdic

    @staticmethod
    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.itervalues():
            sp.set_visible(False)
