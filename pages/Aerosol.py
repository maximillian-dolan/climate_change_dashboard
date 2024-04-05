import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pyhdf.SD import SD, SDC
import os
from datetime import datetime


from data_loader import load_fire_data
fire_all_data, fire_dataframes = load_fire_data()

st.set_page_config(layout="centered")

def read_hdf4_data(file_path, dataset_name):
    """
    Reads specified dataset from an HDF4 file.
    """
    hdf = SD(file_path, SDC.READ)
    dataset = hdf.select(dataset_name)
    data = dataset.get().astype(np.float32)
    hdf.end()
    return data

def aerosol_page():
    st.header("Aerosol Optical Depth Visualization")
    st.write("Explore Aerosol Optical Depth Data.")

    # Create tabs for plots and information
    tab1, tab2 = st.tabs(['Map Visualization', 'Information'])

    with tab1:
        # Checkbox to show fires
        show_fires = st.checkbox(label='Show Fire Data')

        # Set the folder path of HDF file
        aerosol_folder_path = "./aerosol_data/raw_data"

        # Get the list of dates from the file names
        aerosol_dates = [datetime.strptime(f.split('.')[0], '%Y-%m-%d') for f in os.listdir(aerosol_folder_path) if f.endswith('.hdf')]
        aerosol_dates.sort()

        # Create a date selector for the available aerosol data
        selected_date = st.select_slider(
            "Select a date",
            options=aerosol_dates,
            format_func=lambda date: date.strftime('%Y-%m-%d')
        )

        if selected_date:
            date_str = selected_date.strftime('%Y-%m-%d')
            aerosol_file_path = os.path.join(aerosol_folder_path, f"{date_str}.hdf")

            if os.path.exists(aerosol_file_path):
                # Read HDF file
                longitude = read_hdf4_data(aerosol_file_path, 'Longitude')
                latitude = read_hdf4_data(aerosol_file_path, 'Latitude')
                optical_depth = read_hdf4_data(aerosol_file_path, 'Optical_Depth_Land_And_Ocean')

                # Visualization
                fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
                ax.set_extent([-124.48, -114.13, 32.53, 42.01], crs=ccrs.PlateCarree())
                ax.coastlines(resolution='10m')
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.add_feature(cfeature.STATES, linestyle='--')
                
                scatter = ax.scatter(longitude, latitude, c=optical_depth, cmap='viridis', s=10, alpha=0.5, edgecolor='none', transform=ccrs.PlateCarree())
                plt.colorbar(scatter, ax=ax, label='Optical Depth')
                ax.set_title('Aerosol Optical Depth over California')
                
                st.pyplot(fig)

                if show_fires:

                    selected_year = str(selected_date.year)
                    if selected_year in fire_dataframes:
                        fire_df = fire_dataframes[selected_year]
                        fire_df_selected = fire_df[fire_df['acq_date'] == pd.to_datetime(selected_date)]
                        if not fire_df_selected.empty:
                            for index, row in fire_df_selected.iterrows():
                                ax.scatter(row['longitude'], row['latitude'], color='red', s=50, edgecolor='k', transform=ccrs.PlateCarree(), label='Fire' if index == 0 else "")
                            st.pyplot(fig)

    with tab2:
        st.markdown("""
            ## Why is Aerosol data Important?
        """)

def main():
    aerosol_page()

if __name__ == "__main__":
    main()