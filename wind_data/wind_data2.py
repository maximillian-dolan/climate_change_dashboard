from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import cartopy.feature as cfeature
import pandas as pd
import xarray as xr
import datetime
import glob
import os
import rioxarray
import geopandas as gpd
from shapely.geometry import mapping
from shapely.geometry import Point, Polygon

# Check the path
base_directory = ".\wind_data"

# Use os.path.join define all the path
plots_directory = os.path.join(base_directory, "plots")
csv_directory = os.path.join(base_directory, "csv")
daily_csv_directory = os.path.join(csv_directory, "daily")
monthly_csv_directory = os.path.join(csv_directory, "monthly")
monthly_data_directory = os.path.join(base_directory, "raw", "monthly_data")
daily_data_directory = os.path.join(base_directory, "raw", "daily_data")
pro_monthly_data_directory = os.path.join(base_directory, "processed", "monthly_data")
pro_daily_data_directory = os.path.join(base_directory, "processed", "daily_data")

california_boundary_file = "California_County_Boundaries.geojson"


# Make sure directories exist
os.makedirs(plots_directory, exist_ok=True)
os.makedirs(csv_directory, exist_ok=True)
os.makedirs(daily_csv_directory, exist_ok=True)
os.makedirs(monthly_csv_directory, exist_ok=True)
os.makedirs(pro_daily_data_directory, exist_ok=True)
os.makedirs(pro_monthly_data_directory, exist_ok=True)
# Load California boundary
california_gdf = gpd.read_file(california_boundary_file)

# using MERRA-2 data
nc_file_path = 'MERRA2_400.tavg1_2d_flx_Nx.20150801.nc4.nc4'
data = Dataset(nc_file_path,  mode='r')

def date(nc_file_path):
    # Get the range beginning date from the attribute
    date_text = data.RangeBeginningDate
    
    return date_text

date_str = date(nc_file_path)


def read_wind_data(nc_file_path, date_str):
    # Read in the data
    data = Dataset(nc_file_path,  mode='r')
    
    # longitude and latitude
    lons = data.variables['lon']
    lats = data.variables['lat']
    
    ### Might want to return this as well!
    lon, lat = np.meshgrid(lons, lats)

    # 10-meter easterly wind m/s
    U10M = data.variables['ULML']

    # 10-meter northerly wind m/s
    V10M = data.variables['VLML']

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
    # ws_direction = np.arctan2(V10M_nans,U10M_nans)

    # Calculating daily wind speed average 
    ws_daily_avg = np.nanmean(ws, axis=0)

    # Calculating the average daily wind direction
    #U10M_daily_avg = np.nanmean(U10M_nans, axis=0)
    #V10M_daily_avg = np.nanmean(V10M_nans, axis=0)
    #ws_daily_avg_direction = np.arctan2(V10M_daily_avg, U10M_daily_avg)
    # Convert fields to 1D arrays to go into pd dataframe
    lon_1d = lon.flatten()
    lat_1d = lat.flatten()
    ws_daily_avg_1d = ws_daily_avg.flatten()
    #ws_daily_avg_direction_1d = ws_daily_avg_direction.flatten()
    
    # Get array of the date_str the same length as the data
    length = len(ws_daily_avg_1d)
    dates = pd.Series([date_str] * length)

    # Convert to pd dataframe
    wind_df = pd.DataFrame({
    'lon': lon_1d,
    'lat': lat_1d,
    'ws_daily_avg': ws_daily_avg_1d,
    #'ws_daily_avg_direction': ws_daily_avg_direction_1d,
    'date_str': dates
    })
    
    path_csv = os.path.join(daily_csv_directory, f'{date_str}.csv')
    wind_df.to_csv(path_csv)
    
    return wind_df


# Define a function to create and save a precipitation plot with specified settings
def create_wind_plot(ws_daily_avg, ws_daily_avg_direction, date_str, extent=[-125, -113, 32, 42]):
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    # Add state borders to the plot
    ax.add_feature(cfeature.STATES.with_scale('10m'))
    # Plot wind speed data
    #ws_daily_avg.plt(ax=ax, x='lon', y='lat', cmap='viridis', transform=ccrs.PlateCarree())
    #ax.coastlines('10m', edgecolor='black')
    #ax.add_feature(cfeature.BORDERS.with_scale('10m'))
    filename = f"{plots_directory}/wind_{date_str}.png"
    
    # Plot windspeed
    clevs = np.arange(0,14.5,1)
    plt.contourf(lon, lat, ws_daily_avg, clevs, transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
    plt.title(f'Average wind speed on {date_str}')
    cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
    cb.set_label('m/s',size=14,rotation=0,labelpad=15)
    cb.ax.tick_params(labelsize=10)
    # Overlay wind vectors
    #qv = plt.quiver(lon, lat, U10M_daily_avg, V10M_daily_avg, scale=420, color='k')

    # Save the file
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)
    
