import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# -------------------------------------------------------------------
# Importing fire data

# CSV file names
fire_folder_path = './USA_fire_date_2010_2023'
csv_fire_files = [file for file in os.listdir(fire_folder_path) if file.endswith('.csv')]

# Loop through each CSV file and create a dataframe for said file, restricting to rough california coordinates
fire_dataframes = {}
for csv_file in csv_fire_files:
    year = int(csv_file.split('_')[2].split('.')[0])

    whole_fire_df = pd.read_csv(os.path.join(fire_folder_path, csv_file))
    fire_dataframes[f'{year}'] = whole_fire_df[whole_fire_df['latitude'] < 42][whole_fire_df['latitude'] > 33][
        whole_fire_df['longitude'] < -115]

# Format Dataframes
for fire_df in fire_dataframes.values():
    fire_df['month'] = fire_df['acq_date'].apply(lambda x: x[5:7])
    fire_df['confidence'] = fire_df['confidence'] / 100
    fire_df['year'] = fire_df['year'].apply(str)

fire_all_data = pd.concat(fire_dataframes, ignore_index=True)

# prepare fire frequency dataframes
firecount_dataframes = {}

for df in fire_dataframes:
    specific_month_counts = pd.DataFrame(data=fire_dataframes[df].value_counts(subset='month', sort=False))
    specific_month_counts['month names'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                            'September', 'October', 'November', 'December']
    specific_month_counts['year'] = df
    specific_month_counts['count'] = specific_month_counts['count'] / len(fire_dataframes[df])

    firecount_dataframes[df] = specific_month_counts

all_fire_frequencies = pd.concat(firecount_dataframes, ignore_index=True)
# -------------------------------------------------------------------
# Import Temperature data

temp_folder_path = './temperature_data/processed'
csv_temp_files = [file for file in os.listdir(temp_folder_path) if file.endswith('.csv')]

temp_dataframes = {}
for csv_file in csv_temp_files:
    date = csv_file.split('.')[0]

    temp_df = pd.read_csv(os.path.join(temp_folder_path, csv_file))
    temp_df.dropna(inplace=True)  # Drops all points not within California
    temp_df['temperature'] = temp_df['AvgSurfT_tavg'] - 273.15  # Convert from kelvin to celsius
    temp_dataframes[f'{date}'] = temp_df

temp_all_data = pd.concat(temp_dataframes, ignore_index=True)


# -------------------------------------------------------------------
def temperature_page():
    st.header("Temperature Data")
    st.write('Explore temperature data.')

    # Choose date to display
    selected_date_temp = st.select_slider('Select a date',
                                          options=sorted(temp_dataframes.keys(), key=lambda x: x.lower()),
                                          key='fire_date_slider')

    # checkbox to show fires
    show_fires = st.checkbox(label='Show Fire data')

    fire_dataframe = fire_dataframes[
        '2015']  # For now only 2015 temp data is used. If more data added, this will need to be changed

    # Create map
    fig_temperature = px.scatter_mapbox(temp_dataframes[selected_date_temp],
                                        lat='lat',
                                        lon='lon',
                                        # size='temperature',
                                        color='temperature',
                                        color_continuous_scale=px.colors.sequential.thermal,
                                        range_color=(
                                        min(temp_all_data['temperature']), max(temp_all_data['temperature'])),
                                        mapbox_style='open-street-map',
                                        zoom=3.7,
                                        title=f'temperature for {2015}'
                                        )

    # Add fire data
    if show_fires == True:
        fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == selected_date_temp]
        fig_temperature.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                    lat='latitude',
                                                    lon='longitude',
                                                    color_discrete_sequence=['red'] * len(fire_dataframe_date),
                                                    mapbox_style='open-street-map',
                                                    zoom=4,
                                                    title=f'Fire locations'
                                                    ).data[0]
                                  )

    st.plotly_chart(fig_temperature)

    def main():
        temperature_page()

    if __name__ == "__main__":
        main()
