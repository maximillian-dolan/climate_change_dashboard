import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

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

def precipitation_page():
    st.header("Precipitation Data")
    st.write("Explore Precipitation Data.")

    # Line graph
    st.header("Monthly Precipitation Trends")
    precipitation_file_path = "precipitation_data/.csv/monthly_precipitation_summary.csv"
    monthly_precipitation_df = pd.read_csv(precipitation_file_path)
    fig_monthly = px.line(monthly_precipitation_df, x='Month', y='Total Precipitation')
    fig_monthly.update_layout(yaxis_title='Total Precipitation', xaxis_title='Month')
    st.plotly_chart(fig_monthly)

    # daily or monthly data type
    precipitation_data_type = st.radio("Select data type", ('daily', 'monthly'))

    # checkbox to show fires
    show_fires = st.checkbox(label='Show Fire data')

    # set the folder path of csv file
    base_directory = "./precipitation_data"
    precipitation_folder_path = f'./{base_directory}/.csv/{precipitation_data_type}'

    # get the list of file
    precipitation_file_pattern = '%Y-%m-%d' if precipitation_data_type == 'daily' else '%Y-%m'
    precipitation_file_paths = [os.path.join(precipitation_folder_path, f) for f in
                                os.listdir(precipitation_folder_path) if
                                f.endswith('.csv') and datetime.strptime(f.split('.')[0], precipitation_file_pattern)]

    # Get the list of date
    precipitation_dates = [os.path.splitext(f)[0] for f in os.listdir(precipitation_folder_path) if f.endswith('.csv')]
    precipitation_dates = [datetime.strptime(date, precipitation_file_pattern) for date in precipitation_dates]
    precipitation_dates.sort()

    # Create slider
    selected_date = st.select_slider(
        'Select a date',
        options=precipitation_dates,
        format_func=lambda date: date.strftime('%Y-%m-%d' if precipitation_data_type == 'daily' else '%Y-%m'),
        key='precipitation_date_slider'
    )

    # filter by date slider and rough california boundaries
    selected_year = str(selected_date)[:4]
    fire_dataframe = fire_dataframes[selected_year]

    # Select date
    if selected_date:

        # define date_str and precipitation_file_path
        date_str = selected_date.strftime(precipitation_file_pattern)
        precipitation_file_path = os.path.join(precipitation_folder_path, f"{date_str}.csv")

        if os.path.exists(precipitation_file_path):
            # Read csv file
            precipitation_df = pd.read_csv(precipitation_file_path)

            # set the confidence level
            precipitation_confidence_level = 0.95
            precipitation_color_scale_max = precipitation_df[
                'precipitationCal' if precipitation_data_type == 'daily' else 'precipitation'].quantile(
                precipitation_confidence_level)

            # Create map
            fig_precipitation = px.scatter_mapbox(
                precipitation_df,
                lat='lat',
                lon='lon',
                size='precipitationCal' if precipitation_data_type == 'daily' else 'precipitation',
                color='precipitationCal' if precipitation_data_type == 'daily' else 'precipitation',
                color_continuous_scale=px.colors.sequential.Viridis,
                range_color=(0.05, precipitation_color_scale_max),
                mapbox_style='open-street-map',
                zoom=4,
                title=f'Precipitation for {date_str}'
            )

            # create fire plot

            if show_fires == True:
                fire_dataframe_date = fire_dataframe[
                    fire_dataframe['acq_date'] == str(selected_date)[:10]] if precipitation_data_type == 'daily' else \
                fire_dataframe[fire_dataframe['month'] == str(selected_date)[5:7]]
                fig_precipitation.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                              lat='latitude',
                                                              lon='longitude',
                                                              color_discrete_sequence=['red'] * len(
                                                                  fire_dataframe_date),
                                                              mapbox_style='open-street-map',
                                                              zoom=4,
                                                              title=f'Fire locations'
                                                              ).data[0]
                                            )

            # Show
            st.plotly_chart(fig_precipitation)
            # Download button
            # Check file exists
            if os.path.exists(precipitation_file_path):
                # Read file
                with open(precipitation_file_path, "rb") as file:
                    btn = st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=f"{date_str}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("File not found.")
            precipitation_plot_path = f'./{base_directory}/.plots/precipitation_{date_str}.png'
            if os.path.exists(precipitation_plot_path):
                # Read file
                with open(precipitation_plot_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Plot",
                        data=file,
                        file_name=f"precipitation_{date_str}.png",
                        mime="image/png"
                    )
            else:
                st.write("Plot not found.")
def main():
    precipitation_page()



if __name__ == "__main__":
    main()
