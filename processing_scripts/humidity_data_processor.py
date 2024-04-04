import xarray as xr
import pandas as pd
import numpy as np
import os
import geopandas as gpd
from shapely.geometry import mapping

# Setup input and output directories
input_folder_path = '../humidity_data/raw_data/'
output_folder_path = '../humidity/processed_data/'
california_boundary_file = 'California_County_Boundaries.geojson'

# Load California boundary geometry using geopandas
california_gdf = gpd.read_file(california_boundary_file)

# Function to clip data using California boundary
def clip_california_data(ds):
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

# Group files by date
files_by_date = {}
for nc4_file in os.listdir(input_folder_path):
    if nc4_file.endswith('.nc4'):
        # Extract date from filename
        date_str = nc4_file.split('.')[1][1:9]
        if date_str not in files_by_date:
            files_by_date[date_str] = []
        files_by_date[date_str].append(nc4_file)

# Process files for each date
for date_str, files in files_by_date.items():
    daily_datasets = []
    for file in files:
        # Load the dataset
        ds = xr.open_dataset(os.path.join(input_folder_path, file))
        # Clip the dataset using the California boundary
        clipped_ds = clip_california_data(ds)
        daily_datasets.append(clipped_ds)
    
    # Combine datasets for the day and calculate daily mean
    combined_ds = xr.concat(daily_datasets, dim='time')
    daily_mean = combined_ds.mean(dim='time')
    
    daily_mean_humidity = daily_mean['Qair_f_inst']
    
    # Convert to DataFrame
    df = daily_mean_humidity.to_dataframe().reset_index()
    
    # Save to CSV
    formatted_date = pd.to_datetime(date_str).strftime('%Y-%m-%d')
    output_file = os.path.join(output_folder_path, f'{formatted_date}.csv')
    df.to_csv(output_file, index=False)
    
    print(f"Processed and saved data for {formatted_date}")
