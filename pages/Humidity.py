import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime



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

def humidity_page():
    st.header("Humidity Data")
    st.write("Explore Humidity Data")

    humidity_data_type = st.radio("Select Data Type", ('Daily',))

    # Checkbox to show fires
    show_fires = st.checkbox(label='Show Fire Data')

    # Set the folder path of csv file to point directly to the processed data
    base_directory = "./humidity_data/processed_data"
    humidity_folder_path = base_directory

    # Get the list of dates from the file names
    humidity_dates = [
        datetime.strptime(os.path.splitext(f)[0], '%Y-%m-%d') for f in os.listdir(humidity_folder_path) if f.endswith('.csv')
    ]
    humidity_dates.sort()

    # Create slider
    selected_date = st.select_slider(
        'Select a date',
        options=humidity_dates,
        format_func=lambda date: date.strftime('%Y-%m-%d')
    )

    # Filter by date slider
    if selected_date:
        # Define date_str and humidity_file_path
        date_str = selected_date.strftime('%Y-%m-%d')
        humidity_file_path = os.path.join(humidity_folder_path, f"{date_str}.csv")

        if os.path.exists(humidity_file_path):
            # Read csv file
            humidity_df = pd.read_csv(humidity_file_path)

    # Set the confidence level
            humidity_confidence_level = 0.95
            humidity_color_scale_max = humidity_df['Qair_f_inst'].quantile(humidity_confidence_level)

            # Create map
            fig_humidity = px.scatter_mapbox(
                humidity_df,
                lat='lat',
                lon='lon',
                size='Qair_f_inst',
                color='Qair_f_inst',
                color_continuous_scale=px.colors.sequential.Viridis,
                range_color=(humidity_df['Qair_f_inst'].min(), humidity_color_scale_max),
                mapbox_style='open-street-map',
                zoom=5,
                title=f'Humidity for {date_str}'
            )

        if show_fires:
                # Select the appropriate year's fire data
                selected_year = str(selected_date)[:4]
                if selected_year in fire_dataframes:
                    fire_dataframe_date = fire_dataframes[selected_year][fire_dataframes[selected_year]['acq_date'] == str(selected_date)[:10]]
                    fig_humidity.add_trace(px.scatter_mapbox(
                        fire_dataframe_date,
                        lat='latitude',
                        lon='longitude',
                        color_discrete_sequence=['red'] * len(fire_dataframe_date),
                        mapbox_style='open-street-map',
                        zoom=4,
                        title='Fire locations'
                    ).data[0])

        st.plotly_chart(fig_humidity)


# Main layout of the app
def main():
    humidity_page()



if __name__ == "__main__":
    main()


