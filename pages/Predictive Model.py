import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from joblib import load
from sklearn.preprocessing import scale, StandardScaler

# Import common dates of Humidity, precipitation, temperature and wind.
from data_loader import find_common_dates_from_datasets
common_dates = find_common_dates_from_datasets()

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


def predictive():
    st.header('Predictive chart')

    # Stupid way to do it but for now is the only way to only have dates that have all date for currently
    august_2015 = ['2015-08-01', '2015-08-02', '2015-08-03', '2015-08-04', '2015-08-05', '2015-08-06', '2015-08-07',
                   '2015-08-08', '2015-08-09', '2015-08-10', '2015-08-11', '2015-08-12', '2015-08-13', '2015-08-14',
                   '2015-08-15', '2015-08-16', '2015-08-17', '2015-08-18', '2015-08-19', '2015-08-20', '2015-08-21',
                   '2015-08-22', '2015-08-23', '2015-08-24', '2015-08-25', '2015-08-26', '2015-08-27', '2015-08-28',
                   '2015-08-29', '2015-08-30', '2015-08-31']

    # Create slider
    date_predictive = st.select_slider('Select a date', options=august_2015, key='predictive_slider')
    # list(set(temp_dataframes.keys()).intersection(precipitation_dates_predictive)

    data_options = []
    col1, col2 = st.columns([0.75, 0.25])

    with col2:
        predictor_type = st.radio(label='Which predictive model to use',
                                  options=['Random Forest', 'Special Vector Machine'])

    # Import classifier
    if predictor_type == 'Random Forest':
        classifier = load('rf_biased.joblib')
    elif predictor_type == 'Special Vector Machine':
        classifier = load('svc_biased.joblib')
    # classifier = load('rf_classifier.joblib')

    # Add precipitation dataframe
    precipitation_file_path_predictive = os.path.join(precipitation_folder_path_mv, f"{date_predictive}.csv")
    if os.path.exists(precipitation_file_path_predictive):
        precipitation_df_predictive = pd.read_csv(precipitation_file_path_predictive)
        lon_to_longitude(precipitation_df_predictive)
        precipitation_df_predictive['precipitation'] = precipitation_df_predictive['precipitationCal']
        precipitation_df_predictive = precipitation_df_predictive[['latitude', 'longitude', 'precipitation']]
        precipitation_df_predictive = mv_rounder(precipitation_df_predictive, 'precipitation')

        data_options.append('precipitation')

    # Add wind speed dataframe
    wind_file_path_predictive = os.path.join(wind_folder_path, f"{date_predictive}.csv")
    if os.path.exists(wind_file_path_predictive):
        wind_df_predictive = pd.read_csv(wind_file_path_predictive)
        lon_to_longitude(wind_df_predictive)
        wind_df_predictive = wind_df_predictive[wind_df_predictive['SPEEDLML'] != 0]
        wind_df_predictive['wind_speed'] = wind_df_predictive['SPEEDLML']
        wind_df_predictive = wind_df_predictive[['latitude', 'longitude', 'wind_speed']]
        wind_df_predictive = mv_rounder(wind_df_predictive, 'wind_speed')

        data_options.append('wind_speed')

    # Add humidity dataframe
    humidity_file_path_predictive = os.path.join(humidity_folder_path_mv, f"{date_predictive}.csv")
    if os.path.exists(humidity_file_path_predictive):
        humidity_df_predictive = pd.read_csv(humidity_file_path_predictive)
        lon_to_longitude(humidity_df_predictive)
        humidity_df_predictive = humidity_df_predictive[humidity_df_predictive['Qair_f_inst'] != 0]
        humidity_df_predictive['humidity'] = humidity_df_predictive['Qair_f_inst']
        humidity_df_predictive = humidity_df_predictive[['latitude', 'longitude', 'humidity']]
        humidity_df_predictive = mv_rounder(humidity_df_predictive, 'humidity')

        data_options.append('humidity')

    # Add temperature dataframe
    if date_predictive in temp_dataframes:
        temp_df_predictive = temp_dataframes[date_predictive]
        lon_to_longitude(temp_df_predictive)
        temp_df_predictive = temp_df_predictive[['latitude', 'longitude', 'temperature']]
        temp_df_predictive = mv_rounder(temp_df_predictive, 'temperature')

        data_options.append('temperature')

    # Add fire dataframe
    if date_predictive[:4] in fire_dataframes:
        fire_df_predictive = fire_dataframes[date_predictive[:4]]
        fire_df_predictive = fire_df_predictive[fire_df_predictive['acq_date'] == date_predictive]
        with col2:
            show_fires_predictive = st.checkbox(label='Show Fire data')

    else:
        show_fires_predictive = False

    # Merge dataframes into one dataframe
    df_total_predictive = pd.merge(humidity_df_predictive, temp_df_predictive, on=['latitude', 'longitude'])
    if os.path.exists(
            precipitation_file_path_predictive):  # temporary fix for glitch in which data isnt there for precipitation 2010
        df_total_predictive = pd.merge(df_total_predictive, precipitation_df_predictive, on=['latitude', 'longitude'])
    df_total_predictive = pd.merge(df_total_predictive, wind_df_predictive, on=['latitude', 'longitude'])

    data = df_total_predictive[['humidity', 'temperature', 'precipitation', 'wind_speed']]
    df_total_predictive['fire_prediction'] = classifier.predict(StandardScaler().fit_transform(data))
    df_total_predictive[['probability_0', 'probability_1']] = classifier.predict_proba(
        StandardScaler().fit_transform(data))

    predictive_fig = px.scatter_mapbox(df_total_predictive,
                                       lat='latitude',
                                       lon='longitude',
                                       size='probability_1',
                                       hover_name='probability_1',
                                       color_discrete_sequence=['orange'] * len(df_total_predictive),
                                       mapbox_style='open-street-map',
                                       zoom=3.7,
                                       width=500)

    # Add fire data
    if show_fires_predictive == True:
        predictive_fig.add_trace(px.scatter_mapbox(fire_df_predictive,
                                                   lat='latitude',
                                                   lon='longitude',
                                                   color_discrete_sequence=['red'] * len(fire_df_predictive),
                                                   mapbox_style='open-street-map',
                                                   zoom=4,
                                                   title=f'Fire locations'
                                                   ).data[0])
    with col1:
        st.plotly_chart(predictive_fig)
        # st.write(temp_dataframescs.keys())
        # st.write(precip_dates)
        # st.write(df_total_predictive[df_total_predictive['probability_1']>0.1])
        # st.write(df_total_predictive)
def main():
    predictive()

if __name__ == "__main__":

    main()
