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

# Cheak the path
base_directory = "./precipitation_data"

# Use os.path.join define all the path
plots_directory = os.path.join(base_directory, ".plots")
csv_directory = os.path.join(base_directory, ".csv")
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


# Define a function to convert cftime.DatetimeJulian objects to standard datetime.datetime objects
def convert_cftime_datetime(cf_datetime):
    return datetime.datetime(cf_datetime.year, cf_datetime.month, cf_datetime.day,
                             cf_datetime.hour, cf_datetime.minute, cf_datetime.second)


# Define a function to create and save a precipitation plot with specified settings
def create_precipitation_plot(precipitation_dataset, date_str, extent=[-124.4, -114, 32.30, 42]):
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
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
    plt.close(fig)


# To process precipitation data (monthly or daily)
def process_precipitation_data(file_list, save_directory, resolution='monthly'):
    if resolution == 'monthly':
        for file in file_list:
            # Clip data using California boundary
            clipped_ds = clip_california_data(file)

            # Save clipped data
            output_file = os.path.join(save_directory, os.path.basename(file))
            clipped_ds.to_netcdf(output_file)
        new_file_list_monthly = glob.glob(os.path.join(save_directory, "*.nc4"))
        for new_file in new_file_list_monthly:
            # Open the processed dataset
            data = xr.open_dataset(new_file)

            # Select the precipitation data
            precipitation_dataset = data['precipitation'].isel(time=0)
            # Extract the time value
            cf_time_value = precipitation_dataset['time'].values
            # Convert datetime and get datestr
            standard_datetime = convert_cftime_datetime(cf_time_value.item())
            date_str = standard_datetime.strftime('%Y-%m')

            # convert to csv
            df = data.to_dataframe()
            df['precipitation'] = df['precipitation'].fillna(0)
            path_csv = os.path.join(monthly_csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)
            print(f'=== {date_str}.csv saved ===')
            # Create and save the plot
            create_precipitation_plot(precipitation_dataset, date_str)
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

            # Select the precipitationCal data
            precipitation_dataset = data['precipitationCal']

            # Get the date_str
            date_str = precipitation_dataset['time'].dt.strftime('%Y-%m-%d').item()

            # convert to csv
            df = data.to_dataframe()
            df['precipitationCal'] = df['precipitationCal'].fillna(0)
            path_csv = os.path.join(daily_csv_directory, f'{date_str}.csv')
            df.to_csv(path_csv)
            print(f'=== {date_str}.csv saved ===')
            # Create and save the plot
            create_precipitation_plot(precipitation_dataset, date_str)


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


# Get the file list
file_list_monthly = glob.glob(os.path.join(monthly_data_directory, "*.nc4"))
file_list_daily = glob.glob(os.path.join(daily_data_directory, "*.nc4"))

# process monthly data
# process_precipitation_data(file_list_monthly, pro_monthly_data_directory, resolution='monthly')

# process daily data
#process_precipitation_data(file_list_daily, pro_daily_data_directory, resolution='daily')

from datetime import datetime


def annual_and_monthly_precipitation(monthly_csv_directory, csv_directory):
    all_files = os.listdir(monthly_csv_directory)
    monthly_precipitation_sums = {}

    for file_name in all_files:
        try:
            year_month = datetime.strptime(file_name.split(".")[0], "%Y-%m")
        except ValueError:
            continue  # Skip files that don't match the date format

        file_path = os.path.join(monthly_csv_directory, file_name)
        precipitation_df = pd.read_csv(file_path)

        # Sum precipitation for the month
        month_key = year_month.strftime("%Y-%m")
        monthly_precipitation_sums[month_key] = monthly_precipitation_sums.get(month_key, 0) + precipitation_df[
            'precipitation'].sum()

    # Create DataFrame for monthly precipitation sums
    monthly_precip_summary = pd.DataFrame(list(monthly_precipitation_sums.items()),
                                          columns=['Month', 'Total Precipitation'])

    # Create the CSV file path
    monthly_csv_path = os.path.join(csv_directory, 'monthly_precipitation_summary.csv')

    # Save the summary to a CSV file
    monthly_precip_summary.to_csv(monthly_csv_path, index=False)

    return monthly_csv_path

# annual_and_monthly_precipitation(monthly_csv_directory, csv_directory)
new_file_list_daily = glob.glob(os.path.join(pro_daily_data_directory, "*.nc4"))
