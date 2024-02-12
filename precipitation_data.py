import xarray as xr
import matplotlib.pyplot as plt
import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import glob
import os
import pandas as pd
import streamlit as st
from PIL import Image

# Cheak the path
plots_directory = "./.plots"
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)
csv_directory = './.csv'
if not os.path.exists(csv_directory):
    os.makedirs(csv_directory)

# Define a function to retrieve files matching a specific pattern within a directory
def get_file_list_from_directory_glob(directory, pattern="*.nc4"):
    return glob.glob(os.path.join(directory, pattern))


# Define a function to convert cftime.DatetimeJulian objects to standard datetime.datetime objects
def convert_cftime_datetime(cf_datetime):
    return datetime.datetime(cf_datetime.year, cf_datetime.month, cf_datetime.day,
                             cf_datetime.hour, cf_datetime.minute, cf_datetime.second)


# Define a function to create and save a precipitation plot with specified settings
def create_precipitation_plot(precipitation_dataset, date_str, extent=[-124.3, -114.8, 32.30, 42], plots_directory='./.plots'):
     fig = plt.figure(figsize=(10, 8))
     ax = plt.axes(projection=ccrs.PlateCarree())  # PlateCarree projection
     ax.set_extent(extent, crs=ccrs.PlateCarree())
     # Add state borders to the plot
     ax.add_feature(cfeature.STATES.with_scale('10m'))
     # Plot precipitation data
     precipitation_dataset.plot(ax=ax, x='lon', y='lat', cmap='viridis', transform=ccrs.PlateCarree())

     ax.coastlines('10m', edgecolor='black')
     ax.add_feature(cfeature.BORDERS.with_scale('10m'))

     plt.title(f'Precipitation on {date_str}')
     filename = f"{plots_directory}/precipitation_{date_str}.png"
     plt.savefig(filename, bbox_inches='tight')
     #plt.show()  # Display the plot
     plt.close(fig)


# To process precipitation data (monthly or daily)
def process_precipitation_data(file_list, resolution='monthly'):
    if resolution == 'monthly':
        for file in file_list:
            # Open the dataset
            data = xr.open_dataset(file)

            # Select the precipitation data
            precipitation_dataset = data['precipitation'].isel(time=0)
            # Extract the time value
            cf_time_value = precipitation_dataset['time'].values
            # Convert datetime and get datestr
            standard_datetime = convert_cftime_datetime(cf_time_value.item())
            date_str = standard_datetime.strftime('%Y-%m')

            # convert to csv
            df = data.to_dataframe()
            path_csv = os.path.join(csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)

            # Create and save the plot
            create_precipitation_plot(precipitation_dataset, date_str)

    elif resolution == 'daily': # Process daily data
         for file in file_list:
            # Open the dataset
            data = xr.open_dataset(file)

            # Select the precipitationCal data
            precipitation_dataset = data['precipitationCal']

            # Get the date_str
            date_str = precipitation_dataset['time'].dt.strftime('%Y-%m-%d').item()

            # convert to csv
            df = data.to_dataframe()
            path_csv = os.path.join(csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)

            # Create and save the plot
            create_precipitation_plot(precipitation_dataset, date_str)

# Get the file list
directory_path = "./monthly_data"  
file_list_monthly = get_file_list_from_directory_glob(directory_path)

directory_path = "./daily_data"  
file_list_daily = get_file_list_from_directory_glob(directory_path)

# process data and generate plots
#process_precipitation_data(file_list_monthly, resolution='monthly')
process_precipitation_data(file_list_daily, resolution='daily')



