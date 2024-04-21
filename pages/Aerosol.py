import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
from datetime import datetime
import geopandas as gpd

def parse_julian_date(date_str):
    year = int(date_str[1:5])
    day_of_year = int(date_str[5:8])
    return datetime(year, 1, 1) + pd.to_timedelta(day_of_year - 1, unit='d')

def aerosol_page():
    st.header("Aerosol Optical Depth Data")
    st.write("Explore Aerosol Optical Depth Data across California.")

    tab1, tab2 = st.tabs(['plot', 'Information'])

    with tab1:
        aerosol_folder_path = "./Aerosol_data/processed_data"
        
        aerosol_dates = sorted(
            [parse_julian_date(f.split('.')[1]) for f in os.listdir(aerosol_folder_path) if f.startswith('aerosol_data_MYD04_3K')]
        )

        selected_date = st.select_slider(
            'Select a date',
            options=aerosol_dates,
            format_func=lambda date: date.strftime('%Y-%m-%d')
        )

        california_geojson = gpd.read_file('Aerosol_data/california.geojson')  

        if selected_date:
            date_str = selected_date.strftime('%Y-%m-%d')
            aerosol_file_path = None
            for filename in os.listdir(aerosol_folder_path):
                file_date = parse_julian_date(filename.split('.')[1])
                if file_date == selected_date:
                    aerosol_file_path = os.path.join(aerosol_folder_path, filename)
                    break

            if aerosol_file_path and os.path.exists(aerosol_file_path):
                df = pd.read_csv(aerosol_file_path)

                # Clean data: Replace negative and -9999 values
                df['Optical_Depth_Land_And_Ocean'] = df['Optical_Depth_Land_And_Ocean'].replace(-9999.0, np.nan)
                df['Optical_Depth_Land_And_Ocean'] = df['Optical_Depth_Land_And_Ocean'].apply(lambda x: max(x, 0.1) if not pd.isna(x) else np.nan)
                df.dropna(subset=['Optical_Depth_Land_And_Ocean'], inplace=True)

                # Filter data within California boundaries
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
                gdf = gdf[gdf.geometry.within(california_geojson.unary_union)]

                if not gdf.empty:
                    optical_depth_max = gdf['Optical_Depth_Land_And_Ocean'].quantile(0.95)
                    optical_depth_min = gdf['Optical_Depth_Land_And_Ocean'].min()

                    fig_aerosol = px.scatter_mapbox(
                        gdf,
                        lat='Latitude',
                        lon='Longitude',
                        size='Optical_Depth_Land_And_Ocean',
                        color='Optical_Depth_Land_And_Ocean',
                        color_continuous_scale=px.colors.sequential.Viridis,
                        labels={'Optical_Depth_Land_And_Ocean': 'Aerosol Depth'},
                        range_color=(optical_depth_min, optical_depth_max),
                        mapbox_style='open-street-map',
                        zoom=4,
                        title=f'Aerosol Optical Depth for {date_str}'
                    )
                    st.plotly_chart(fig_aerosol)
                else:
                    st.error("No valid data available for the selected date. Please try another date.")
            else:
                st.error("File not found. Please check the file path or availability.")

    with tab2:
        st.markdown("""
            ## Why is Aerosl data Important?
            """)

def main():
    aerosol_page()

if __name__ == "__main__":
    main()
