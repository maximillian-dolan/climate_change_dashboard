from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import cartopy.feature as cfeature

# using MERRA-2 data

data = Dataset('wind4.nc4',  mode='r')

# longitude and latitude
lons = data.variables['lon']
lats = data.variables['lat']
lon, lat = np.meshgrid(lons, lats)

# 10-meter easterly wind m/s
U10M = data.variables['U10M']

# 10-meter northerly wind m/s
V10M = data.variables['V10M']

# Replacing 0's with NaN
U10M_nans = U10M[:]
V10M_nans = V10M[:]
_FillValueU10M = U10M._FillValue
_FillValueV10M = V10M._FillValue
U10M_nans[U10M_nans == _FillValueU10M] = np.nan
V10M_nans[V10M_nans == _FillValueV10M] = np.nan

# Calculating the wind speed vector
ws = np.sqrt(U10M_nans**2+V10M_nans**2)

# Calcluating the wind direction in radians
ws_direction = np.arctan2(V10M_nans,U10M_nans)

# Calculating daily wind speed average
ws_daily_avg = np.nanmean(ws, axis=0)

# Calculating the average daily wind direction
U10M_daily_avg = np.nanmean(U10M_nans, axis=0)
V10M_daily_avg = np.nanmean(V10M_nans, axis=0)
ws_daily_avg_direction = np.arctan2(V10M_daily_avg, U10M_daily_avg)



# Set the extent of the plot to be California
extent = [-124.3, -114.8, 32.30, 42]
# Set the figure size, projection, and extent
fig = plt.figure(figsize=(10,8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent, crs=ccrs.PlateCarree())  

# Add state borders to the plot
ax.add_feature(cfeature.STATES.with_scale('10m'))
ax.coastlines('10m', edgecolor='black')
ax.add_feature(cfeature.BORDERS.with_scale('10m'))

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='black', linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlines = True
gl.xlocator = mticker.FixedLocator([-65,-60,-50,-40,-30])
gl.ylocator = mticker.FixedLocator([30,40,50,60])
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size':10, 'color':'black'}
gl.ylabel_style = {'size':10, 'color':'black'}

# Plot windspeed
clevs = np.arange(0,14.5,1)
plt.contourf(lon, lat, ws[0,:,:], clevs, transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
plt.title('10m Wind Speed and Direction, 1 Jan 2015', size=16)
cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
cb.set_label('m/s',size=14,rotation=0,labelpad=15)
cb.ax.tick_params(labelsize=10)
# Overlay wind vectors
qv = plt.quiver(lon, lat, U10M_nans[0,:,:], V10M_nans[0,:,:], scale=420, color='k')

# Save the file
## NEEDS TO BE CHANGED to work for lots of plots
fig.savefig('MERRA2_10m_ws.png', format='png', dpi=120)