import streamlit as st
import pandas as pd
import plotly.express as px
import os
from data_loader import generate_dates

st.set_page_config(layout="centered")

def lon_to_longitude(df):
    '''
    Simple function to add latitude and longitude columns if dataframe only contains columns labeled lon and lat
    '''
    if 'lon' in df.columns:
        df['longitude'] = df['lon']

    if 'lat' in df.columns:
        df['latitude'] = df['lat']


def mv_rounder(df, feature):
    '''
    Simple function to round latitude and longitude to nearest 0.5, and drop duplicates (averaging value in feature between duplicates).
    Note that latitude and longitude columns must be named 'latitude' and 'longitude' not 'lat' and 'lon'.
    '''

    if ('latitude' and 'longitude') in df.columns:
        df['longitude'] = df['longitude'].apply(lambda x: round(x))
        df['latitude'] = df['latitude'].apply(lambda x: round(x))
        df = df.groupby(['latitude', 'longitude']).agg({feature: 'mean'}).reset_index()

        return df

# Define path
humidity_folder_path_mv = "./humidity_data/processed_data"
precipitation_folder_path_mv = './precipitation_data/.csv/daily'
wind_folder_path = './wind_data/wind_data/csv/daily'

# Import temp_dataframes and fire_dataframes
from data_loader import load_and_process_temperature_data, load_fire_data
temp_all_data, temp_dataframes = load_and_process_temperature_data()
fire_all_data, fire_dataframes = load_fire_data()

def multivariable_graph():
    st.header('Multivariable visualisation')

    # Create slider
    date_mv = st.select_slider('Select a date', options=generate_dates('2010-01-02','2023-12-31'),
                               key='mv_slider')

    data_options = []
    col1, col2 = st.columns([0.75, 0.25])

    # Add precipitation dataframe
    precipitation_file_path_mv = os.path.join(precipitation_folder_path_mv, f"{date_mv}.csv")
    if os.path.exists(precipitation_file_path_mv):
        precipitation_df_mv = pd.read_csv(precipitation_file_path_mv)
        lon_to_longitude(precipitation_df_mv)
        precipitation_df_mv['precipitation'] = precipitation_df_mv['precipitationCal']
        precipitation_df_mv = precipitation_df_mv[['latitude', 'longitude', 'precipitation']]
        precipitation_df_mv = mv_rounder(precipitation_df_mv, 'precipitation')

        data_options.append('precipitation')

    # Add wind speed dataframe
    wind_file_path_mv = os.path.join(wind_folder_path, f"{date_mv}.csv")
    if os.path.exists(wind_file_path_mv):
        wind_df_mv = pd.read_csv(wind_file_path_mv)
        lon_to_longitude(wind_df_mv)
        wind_df_mv = wind_df_mv[wind_df_mv['SPEEDLML'] != 0]
        wind_df_mv['wind_speed'] = wind_df_mv['SPEEDLML']
        wind_df_mv = wind_df_mv[['latitude', 'longitude', 'wind_speed']]
        wind_df_mv = mv_rounder(wind_df_mv, 'wind_speed')

        data_options.append('wind_speed')

    # Add humidity dataframe
    humidity_file_path_mv = os.path.join(humidity_folder_path_mv, f"{date_mv}.csv")
    if os.path.exists(humidity_file_path_mv):
        humidity_df_mv = pd.read_csv(humidity_file_path_mv)
        lon_to_longitude(humidity_df_mv)
        humidity_df_mv = humidity_df_mv[humidity_df_mv['Qair_f_inst'] != 0]
        humidity_df_mv['humidity'] = humidity_df_mv['Qair_f_inst']
        humidity_df_mv = humidity_df_mv[['latitude', 'longitude', 'humidity']]
        humidity_df_mv = mv_rounder(humidity_df_mv, 'humidity')

        data_options.append('humidity')

    # Add temperature dataframe
    if date_mv in temp_dataframes:
        temp_df_mv = temp_dataframes[date_mv]
        lon_to_longitude(temp_df_mv)
        temp_df_mv = temp_df_mv[['latitude', 'longitude', 'temperature']]
        temp_df_mv = mv_rounder(temp_df_mv, 'temperature')

        data_options.append('temperature')

    # Add fire dataframe
    if date_mv[:4] in fire_dataframes:
        fire_df_mv = fire_dataframes[date_mv[:4]]
        fire_df_mv = fire_df_mv[fire_df_mv['acq_date'] == date_mv]
        with col2:
            show_fires_mv = st.checkbox(label='Show Fire data')

    else:
        show_fires_mv = False

    # Merge dataframes into one dataframe
    df_total_mv = temp_df_mv # Temperature has data for every day
    if os.path.exists(humidity_file_path_mv):
        df_total_mv = pd.merge(humidity_df_mv, df_total_mv, on=['latitude', 'longitude'])
    if os.path.exists(precipitation_file_path_mv):
        df_total_mv = pd.merge(df_total_mv, precipitation_df_mv, on=['latitude', 'longitude'])
    if os.path.exists(wind_file_path_mv):
        df_total_mv = pd.merge(df_total_mv, wind_df_mv, on=['latitude', 'longitude'])

    with col2:
        color_mv = st.selectbox(label='Color', options=data_options)
        size_mv = st.selectbox(label='Size', options=data_options)

    multivariable_fig = px.scatter_mapbox(df_total_mv,
                                          lat='latitude',
                                          lon='longitude',
                                          size=size_mv if size_mv != 'temperature' else df_total_mv['temperature']+min(df_total_mv['temperature']), #fixes error trying to set size to negative value
                                          hover_name=size_mv,
                                          color=color_mv,
                                          color_continuous_scale=px.colors.sequential.thermal,
                                          # range_color=(min(temp_all_data['temperature']), max(temp_all_data['temperature'])),
                                          mapbox_style='open-street-map',
                                          zoom=3.7,
                                          width=500)

    # Add fire data
    if show_fires_mv == True and len(fire_df_mv) != 0:
        multivariable_fig.add_trace(px.scatter_mapbox(fire_df_mv,
                                                      lat='latitude',
                                                      lon='longitude',
                                                      color_discrete_sequence=['red'] * len(fire_df_mv),
                                                      mapbox_style='open-street-map',
                                                      zoom=4,
                                                      title=f'Fire locations'
                                                      ).data[0])
    with col1:
        st.plotly_chart(multivariable_fig)

def main():
    multivariable_graph()

if __name__ == "__main__":

    main()
