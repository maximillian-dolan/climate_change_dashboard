import xarray as xr
import matplotlib.pyplot as plt
import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import glob
import os
import pandas as pd
import rioxarray
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np
nc_file_path = 'MERRA2_400.inst1_2d_lfo_Nx.20150801.nc4.nc4'

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

# Define a function to retrieve files matching a specific pattern within a directory
def get_file_list_from_directory_glob(directory, pattern="*.nc4"):
    return glob.glob(os.path.join(directory, pattern))

#wind_data = xr.open_dataset(nc_file_path)
#california_boundary_file = "California_County_Boundaries.geojson"
#california_gdf = gpd.read_file(california_boundary_file)



# Get the date_str
#date_str = ds['time'].dt.strftime('%Y-%m-%d').item()
# Get the date string
def date(cf_datetime):
    print(cf_datetime)
    # Get the range beginning date from the attribute
    date_text = cf_datetime.RangeBeginningDate
    
    return date_text

#date_str = date(nc_file_path)
# Define a function to convert cftime.DatetimeJulian objects to standard datetime.datetime objects
#def convert_cftime_datetime(cf_datetime):
    #return datetime.datetime(cf_datetime.year, cf_datetime.month, cf_datetime.day,
                             #cf_datetime.hour, cf_datetime.minute, cf_datetime.second)
#date_str = date(wind_data)

# To process wind data (monthly or daily)
def process_wind_data(file_list, save_directory, resolution='monthly'):
    if resolution == 'monthly':
        for file in file_list:
            print(f"Processing file: {file}")  # Print the name of the file being processed
            # Clip data using California boundary
            clipped_ds = clip_california_data(file)
            #print(clipped_ds)
            # Save clipped data
            output_file = os.path.join(save_directory, os.path.basename(file))
            clipped_ds.to_netcdf(output_file)
        new_file_list_monthly = glob.glob(os.path.join(save_directory, "*.nc4"))
        for new_file in new_file_list_monthly:
            # Open the processed dataset
            data = xr.open_dataset(new_file)
            #print(new_file)
            # Select the wind data
            wind_dataset = data['SPEEDLML'].isel(time=0)
            # Extract the time value
            #cf_time_value = wind_dataset['time'].values
            # Convert datetime and get datestr
            #standard_datetime = date(cf_time_value.item())
            #date_str = standard_datetime.strftime('%Y-%m')
            #date_str = wind_dataset.RangeBeginningDate
            # Assuming wind_dataset is your xarray Dataset
            date_str = wind_dataset.time.dt.strftime('%Y-%m-%d').values


            # Convert the first date to a string
            #date_str = dates[0]
            
            # convert to csv
            df = data.to_dataframe()
            df['SPEEDLML'] = df['SPEEDLML'].fillna(0)
            path_csv = os.path.join(monthly_csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)
            print(f'=== {date_str}.csv saved ===')
            # Create and save the plot
            create_wind_plot(data, date_str)
    elif resolution == 'daily':  # Process daily data
        for file in file_list:
            # Clip data using California boundary
            clipped_ds = clip_california_data(file)

            # Save clipped data
            output_file = os.path.join(save_directory, os.path.basename(file))
            clipped_ds.to_netcdf(output_file)

        new_file_list_daily = glob.glob(os.path.join(save_directory, "*.nc4"))

        for new_file in new_file_list_daily:
            # Open the dataset
            data = xr.open_dataset(new_file)

            # Select the wind data from data
            wind_dataset = data['SPEEDLML'].isel(time=0)

            # Get the date_str
            date_str = wind_dataset.time.dt.strftime('%Y-%m-%d').values

            # convert to csv
            df = data.to_dataframe()
            df['SPEEDLML'] = df['SPEEDLML'].fillna(0)
            path_csv = os.path.join(daily_csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)
            print(f'=== {date_str}.csv saved ===')
            # Create and save the plot
            create_wind_plot(data, date_str)


# Function to clip data using California boundary
def clip_california_data(nc_file_path):
    ds = xr.open_dataset(nc_file_path)
    if 'time_bnds' in ds.variables:
        ds = ds.drop_vars('time_bnds')
    ds = ds.rio.write_crs("EPSG:4326")
    ds = ds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    california_geometry = [mapping(shp) for shp in california_gdf.geometry]
    clipped_ds = ds.rio.clip(california_geometry, ds.rio.crs)
    for var in clipped_ds.variables:
        if 'grid_mapping' in clipped_ds[var].attrs:
            del clipped_ds[var].attrs['grid_mapping']
    return clipped_ds

# clipped_ds = clip_california_data(nc_file_path)
# print(clipped_ds)
# Access the wind component variables from the xarray dataset
#ULML = clipped_ds['ULML']
#VLML = clipped_ds['VLML']


            
#wind_speed = np.sqrt(ULML**2 + VLML**2)
#wind_speed = clipped_ds['SPEEDLML']

# Add the wind speed variable to the xarray dataset
#clipped_ds['wind_speed'] = wind_speed

# Compute the average wind speed along the time dimension
#avg_wind_speed = clipped_ds['wind_speed'].mean(dim='time')


# Plot the California boundary
#fig, ax = plt.subplots(figsize=(10, 8))
#california_gdf.plot(ax=ax, color='none', edgecolor='black')

# Plot the average wind speed data on the same plot
#im = avg_wind_speed.plot.imshow(ax=ax, cmap='viridis', add_colorbar=False)

# Add colorbar
#cbar = fig.colorbar(im, ax=ax, label='Wind Speed (m/s)')

# Set title and labels
#plt.title('Average Wind Speed in California')
#plt.xlabel('Longitude')
#plt.ylabel('Latitude')

# Show the plot
#plt.show()

#def date(nc_file_path):
    #date_text = data.RangeBeginningDate
    
    #return date_text

#date_str = date(nc_file_path)


# Define a function to create and save a wind plot
def create_wind_plot(wind_dataset, date_str, extent=[-125, -113, 32, 42]):
    # Compute the average wind speed along the time dimension
    # print(wind_dataset)
    wind_speed = wind_dataset['SPEEDLML']
    avg_wind_speed = wind_speed.mean(dim='time')


    # Plot the California boundary
    fig, ax = plt.subplots(figsize=(10, 8))
    california_gdf.plot(ax=ax, color='none', edgecolor='black')

    # Plot the average wind speed data on the same plot
    im = avg_wind_speed.plot.imshow(ax=ax, cmap='viridis', add_colorbar=False)

    # Add colorbar
    cbar = fig.colorbar(im, ax=ax, label='Wind Speed (m/s)')

    # Set title and labels
    plt.title(f'Average wind speed on {date_str}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Show the plot
    #plt.show()
    
    # Plot windspeed
    #clevs = np.arange(0,14.5,1)
    #plt.contourf(lon, lat, ws_daily_avg, clevs, transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
    
    #cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
    #cb.set_label('m/s',size=14,rotation=0,labelpad=15)
    #cb.ax.tick_params(labelsize=10)
    # Overlay wind vectors
    #qv = plt.quiver(lon, lat, U10M_daily_avg, V10M_daily_avg, scale=420, color='k')

    # Save the file
    filename = f"{plots_directory}/wind_{date_str}.png"
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)
    
# Get the file list
file_list_monthly = glob.glob(os.path.join(monthly_data_directory, "*.nc4"))
file_list_daily = glob.glob(os.path.join(daily_data_directory, "*.nc4"))

# Process monthly wind data
process_wind_data(file_list_monthly, pro_monthly_data_directory, resolution='monthly')

# Process daily wind data
process_wind_data(file_list_daily, pro_daily_data_directory, resolution='daily')