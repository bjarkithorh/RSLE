import pandas as pd
import numpy as np
import gdal
import matplotlib as mplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import datetime
from datetime import datetime
 
#Import the result file and set it up as a Pandas dataframe
result = pd.read_csv("020.D8Z.csv", header=0, sep=',',  index_col  = [0])
result.index = pd.to_datetime(result.index)

years = mdates.YearLocator()
months = mdates.MonthLocator(bymonth=9, bymonthday=1, interval=1, tz=None)

fig = plt.figure(figsize=(17,11))
plt.subplots_adjust(left=None, bottom=None, right=None, top=0.85)

ax1 = plt.subplot2grid((14,6),(0,0), colspan=5, rowspan=3)
ax1.title.set_text('Titill')
ax1.plot(result.index, result['S_RSLE'], 'b-')
ax1.scatter(result.index, result['M_RSLE_70pC'], s=10)
plt.ylabel('RSLE mas', fontsize=12)
ax1.xaxis.set_major_locator(months)
ax1.tick_params(labelsize=8)
ylimmax = result['M_RSLE'].max()+300
plt.ylim(0, ylimmax)
ax1.patch.set_facecolor('none')
plt.grid()

ax2 = plt.subplot2grid((14,6),(3,0), colspan=5, rowspan=2, sharex=ax1)
ax2.bar(result.index, result['S_rrsc'], color='green', edgecolor='green')
plt.ylabel('RRSC mm/day', fontsize=12)
ax21 = ax2.twinx()
ax21.plot(result.index, result['S_swe'], 'b')
ax21.fill_between(result.index, 0, result['S_swe'], facecolor='blue', alpha=0.3)
for tl in ax21.get_yticklabels():
    tl.set_color('black')
plt.ylabel('SWE mm', fontsize=12)
ax2.tick_params(labelsize=8)
ax21.tick_params(labelsize=8)
ax2.patch.set_facecolor('none')
ax2.set_zorder(10)
ax21.set_zorder(3)
ax21.grid(True)
ax2.grid(True)
plt.grid()

ax3 = plt.subplot2grid((14,6),(5,0), colspan=5, rowspan=2, sharex=ax1)
mix_temp = result['S_temp'].as_matrix()
lower_temp = np.ma.masked_where(mix_temp > 0, mix_temp)
upper_temp = np.ma.masked_where(mix_temp <= 0, mix_temp)
ax3.bar(result.index, upper_temp, color='red', edgecolor='red')
ax3.bar(result.index, lower_temp, color='blue', edgecolor='blue')
ax3.tick_params(labelsize=8)
plt.ylabel('Temperature C', fontsize=12)
plt.axhline(0, color='g')
ax3.patch.set_facecolor('none')
plt.grid()

ax4 = plt.subplot2grid((14,6),(7,0), colspan=5, rowspan=2)
ax4.plot(result.index, result['gwb_q'])
ax4.tick_params(labelsize=8)
plt.ylabel('Runoff mm', fontsize=12)
ax4.patch.set_facecolor('none')
ax4.xaxis.set_major_locator(months)
plt.grid()

"""
cdme2 = gdal.Open('norgedem500align.tif')
norge = np.array(cdme2.GetRasterBand(1).ReadAsArray())

ax5 = plt.subplot2grid((8,6),(5,0), colspan=1, rowspan=2)
ax5.matshow(norge, vmin=0, vmax=3000)
plt.axis('off')
plt.xlabel('Norway')


cdme = gdal.Open('norgedem_1000m_catchm.tif')
elev = np.array(cdme.GetRasterBand(1).ReadAsArray())
"""
ax6 = plt.subplot2grid((14,6),(9,1), colspan=1, rowspan=3)
ax6.text(1, 1, "Text describing the various things we se in he graph", fontsize=10, withdash=True)
plt.axis('off')

ax7 = plt.subplot2grid((14,6),(9,0), colspan=1, rowspan=3)
ax7.scatter(result['S_RSLE70pC'], result['M_RSLE_70pC'])
ax7.tick_params(labelsize=7)
plt.xticks(rotation='vertical')

#plt.subplots_adjust(left=None, bottom=None, right=None, top=0.85)

plt.tight_layout(pad=0.5)
# when saving, specify the DPI
fig.savefig("myplot.png", dpi = 150, orientation='portrait', bbox_inches='tight')
print('Tilbuid')