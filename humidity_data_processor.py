import xarray as xr
import pandas as pd
import numpy as np
import os
import geopandas as gpd
from shapely.geometry import mapping

# Load the NetCDF file
input_folder_path = './humidity/raw'
output_folder_path = './humidity/processed/'
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

humidity_datasets = {}
humidity_dataframes = {}

# Load datasets into dictionary, indexing my date
for nc4_file in nc4_files:
        
    date = nc4_file.split('.')[1][1:]
    ds = xr.open_dataset(os.path.join(input_folder_path, nc4_file))
    
    humidity_datasets[f'{date}'] = ds


# Turn each dataset into a dataframe containing the data, latitude, longitude and humidity
for date, ds in humidity_datasets.items():
    
    # Clip data using California boundary
    clipped_ds = clip_california_data(ds)
    print(f'{date} succesfully clipped')

    # Access the 'Qair_f_inst' variable
    specific_humidity_variable = clipped_ds['Qair_f_inst']
    
    # Convert the variable to a pandas DataFrame
    df = specific_humidity_variable.to_dataframe(name='Qair_f_inst')
    
    # Turn lat,lon,date date (currently used as index) to columns
    other_data = df.index.to_frame(index = True)   
    df = pd.concat([df,other_data], axis = 1)
    
    # Add new index, ordering just by rows
    df['index'] = np.arange(len(df))
    df.set_index('index', inplace=True)
    
    # Format time to be date string instead of datetime object
    df['time'] = df['time'].apply(str).apply(lambda x: x[:10])

    
    humidity[f'{date}'] = df

# Save dataframes to processed folder 
for date, df in humidity_dataframes.items():
    date = date[:4] + '-' +  date[4:6] + '-' + date[6:]
    df.to_csv(output_folder_path+date+'.csv')
