#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 22:13:47 2024

@author: maxdolan
"""

import xarray as xr
import pandas as pd
import numpy as np
import os
import geopandas as gpd
from shapely.geometry import mapping

# Load the NetCDF file
input_folder_path = '../temperature_data/raw'
output_folder_path = '../temperature_data/processed/'
california_boundary_file = "California_County_Boundaries.geojson"

nc4_files = [file for file in os.listdir(input_folder_path) if file.endswith('.nc4')]
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

temperature_datasets = {}
temperature_dataframes = {}

# Load datasets into dictionary, indexing my date
for nc4_file in nc4_files:
        
    date = nc4_file.split('.')[1][1:]
    ds = xr.open_dataset(os.path.join(input_folder_path, nc4_file))
    
    temperature_datasets[f'{date}'] = ds


# Turn each dataset into a dataframe containing the data, latitude, longitude and temperature
for date, ds in temperature_datasets.items():
    
    # Clip data using California boundary
    clipped_ds = clip_california_data(ds)
    print(f'{date} succesfully clipped')

    # Access the 'AvgSurfT_tavg' variable
    avg_surface_temperature_var = clipped_ds['AvgSurfT_tavg']
    
    # Convert the variable to a pandas DataFrame
    df = avg_surface_temperature_var.to_dataframe(name='AvgSurfT_tavg')
    
    # Turn lat,lon,date date (currently used as index) to columns
    other_data = df.index.to_frame(index = True)   
    df = pd.concat([df,other_data], axis = 1)
    
    # Add new index, ordering just by rows
    df['index'] = np.arange(len(df))
    df.set_index('index', inplace=True)
    
    # Format time to be date string instead of datetime object
    df['time'] = df['time'].apply(str).apply(lambda x: x[:10])

    
    temperature_dataframes[f'{date}'] = df

# Save dataframes to processed folder 
for date, df in temperature_dataframes.items():
    date = date[:4] + '-' +  date[4:6] + '-' + date[6:]
    df.to_csv(output_folder_path+date+'.csv')





    
