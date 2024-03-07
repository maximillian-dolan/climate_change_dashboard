import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime


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

#-------------------------------------------------------------------
# Importing fire data

# CSV file names
fire_folder_path = './USA_fire_date_2010_2023'
csv_fire_files = [file for file in os.listdir(fire_folder_path) if file.endswith('.csv')]

# Loop through each CSV file and create a dataframe for said file, restricting to rough california coordinates
fire_dataframes = {}
for csv_file in csv_fire_files:

    year = int(csv_file.split('_')[2].split('.')[0])
    
    whole_fire_df = pd.read_csv(os.path.join(fire_folder_path, csv_file))
    fire_dataframes[f'{year}'] = whole_fire_df[whole_fire_df['latitude'] < 42][whole_fire_df['latitude']>33][whole_fire_df['longitude']<-115]

# Format Dataframes
for fire_df in fire_dataframes.values():
    fire_df['month'] = fire_df['acq_date'].apply(lambda x: x[5:7])
    fire_df['confidence'] = fire_df['confidence']/100
    fire_df['year'] = fire_df['year'].apply(str)

fire_all_data = pd.concat(fire_dataframes, ignore_index=True)

# prepare fire frequency dataframes
firecount_dataframes = {}

for df in fire_dataframes:
    specific_month_counts = pd.DataFrame(data = fire_dataframes[df].value_counts(subset = 'month', sort = False))
    specific_month_counts['month names'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    specific_month_counts['year'] = df
    specific_month_counts['count'] = specific_month_counts['count']/len(fire_dataframes[df])

    firecount_dataframes[df] = specific_month_counts

all_fire_frequencies = pd.concat(firecount_dataframes, ignore_index=True)

def fire_page():
    st.header("Fire Occurence Data")
    st.write("data and visualizations")

    #Create tabs for two plots
    tab1, tab2 = st.tabs(['locations','frequency'])

    #Create fire locations plot
    with tab1:

        fire_data_type = st.radio('select data type',('monthly','yearly'))

        if fire_data_type == 'monthly':
            fire_year = st.select_slider('year', options = fire_dataframes.keys())
            fire_df_chosen = fire_dataframes[fire_year]

        if fire_data_type == 'monthly':

            fig_fire = px.scatter_mapbox(fire_df_chosen,
                                    lat='latitude',
                                    lon='longitude',
                                    color_discrete_sequence=['red']*len(fire_df),
                                    mapbox_style='open-street-map',
                                    zoom=3,
                                    hover_name = 'confidence',
                                    opacity = fire_df_chosen['confidence'],
                                    animation_frame = 'month',
                                    title=f'Fire locations')

        if fire_data_type == 'yearly':
            fig_fire = px.scatter_mapbox(fire_all_data,
                                    lat='latitude',
                                    lon='longitude',
                                    color_discrete_sequence=['red']*len(fire_df),
                                    mapbox_style='open-street-map',
                                    zoom=3,
                                    hover_name = 'confidence',
                                    opacity = fire_all_data['confidence'],
                                    animation_frame = 'year',
                                    title=f'Fire locations') 
        
        st.plotly_chart(fig_fire)
        
    # Create fire frequency chart
    fire_frequency_chart = px.bar(data_frame = all_fire_frequencies,
                                        x = 'month names',
                                        y = 'count',
                                        hover_name = 'month names',
                                        animation_frame  = 'year',
                                        animation_group = 'month names',
                                        range_y = [0,0.7],
                                        color_discrete_sequence = ['red']*len(all_fire_frequencies))

    with tab2:
        st.plotly_chart(fire_frequency_chart)

        

# Main layout of the app
def main():
    fire_page()
if __name__ == "__main__":
    main()


