import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
# Import wind chart
from data_loader import create_wind_chart
# Import fire data
from data_loader import load_fire_data
fire_all_data, fire_dataframes = load_fire_data()

st.set_page_config(layout="centered")

def wind_page():
    st.header("Wind Data")
    st.write('Explore wind data.')
    # Create tabs for two plots
    tab1, tab2, tab3 = st.tabs(['Plot', 'Line graph', 'Information'])
    with tab1:
        # daily or monthly data type
        wind_data_type = st.radio("Select data type", ('daily',))

        # checkbox to show fires
        show_fires = st.checkbox(label = 'Show Fire data')

        # set the folder path of csv file
        base_directory = "./wind_data/wind_data"
        wind_folder_path = f'./{base_directory}/csv/{wind_data_type}'

        # get the list of file
        wind_file_pattern = '%Y-%m-%d' if wind_data_type == 'daily' else '%Y-%m'
        wind_file_paths = [os.path.join(wind_folder_path, f) for f in
                                    os.listdir(wind_folder_path) if
                                    f.endswith('.csv') and datetime.strptime(f.split('.')[0], wind_file_pattern)]

        # Get the list of date
        wind_dates = [os.path.splitext(f)[0] for f in os.listdir(wind_folder_path) if f.endswith('.csv')]
        wind_dates = [datetime.strptime(date, wind_file_pattern) for date in wind_dates]
        wind_dates.sort()

        # Create slider
        selected_date = st.select_slider(
            'Select a date',
            options=wind_dates,
            format_func=lambda date: date.strftime('%Y-%m-%d' if wind_data_type == 'daily' else '%Y-%m'),
            key='wind_date_slider'
        )

        # filter by date slider and rough california boundaries
        selected_year = str(selected_date)[:4]
        fire_dataframe = fire_dataframes[selected_year]



        # Select date
        if selected_date:

            # define date_str and wind_file_path
            date_str = selected_date.strftime(wind_file_pattern)
            wind_file_path = os.path.join(wind_folder_path, f"{date_str}.csv")

            if os.path.exists(wind_file_path):
                # Read csv file
                wind_df = pd.read_csv(wind_file_path)
                wind_df.rename(columns={'SPEEDLML': 'Wind Speed (m/s)'}, inplace=True)

                # set the confidence level
                wind_confidence_level = 0.95
                wind_color_scale_max = wind_df[
                    'Wind Speed (m/s)' if wind_data_type == 'daily' else 'wind'].quantile(
                    wind_confidence_level)

                # Create map
                fig_wind = px.scatter_mapbox(
                    wind_df,
                    lat='lat',
                    lon='lon',
                    size='Wind Speed (m/s)' if wind_data_type == 'daily' else 'wind',
                    color='Wind Speed (m/s)' if wind_data_type == 'daily' else 'wind',
                    color_continuous_scale=px.colors.sequential.Viridis_r,
                    range_color=(0.05, wind_color_scale_max),
                    mapbox_style='open-street-map',
                    zoom=3.7,
                    title=f'Wind for {date_str}'
                )

                # create fire plot

                if show_fires == True:
                    fire_dataframe_date = fire_dataframe[
                        fire_dataframes[selected_year]['acq_date'] == str(selected_date)[:10]]
                    if not fire_dataframe_date.empty:
                        fig_wind.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                                    lat='latitude',
                                                                    lon='longitude',
                                                                    color_discrete_sequence=['red'] * len(
                                                                        fire_dataframe_date),
                                                                    mapbox_style='open-street-map',
                                                                    zoom=4,
                                                                    title=f'Fire locations'
                                                                    ).data[0]
                                                  )
                    else:
                        st.warning(f"No fire data available for {date_str}.")
                # Show
                st.plotly_chart(fig_wind)
                # Download button
                # Check file exists
                if os.path.exists(wind_file_path):
                    # Read file
                    with open(wind_file_path, "rb") as file:
                        btn = st.download_button(
                            label="Download CSV",
                            data=file,
                            file_name=f"{date_str}.csv",
                            mime="text/csv"
                        )
                else:
                    st.write("File not found.")
    with tab2:
        fig_wind_chart = create_wind_chart()
        st.plotly_chart(fig_wind_chart, use_container_width=True)
    with tab3:
        st.markdown("""
            ## Why is Wind Data Important?
            Stronger wind speeds can significantly enhance the rate at which fire spreads and can carry embers or flames across vast distances. This, in turn, can ignite new areas and cause fires to spread more rapidly than they would in the absence of wind. Additionally, wind amplifies the amount of oxygen available to the flames, intensifying the fire. Wind often accompanies low humidity, which can dry out vegetation, thereby making it more flammable. This increases the risk of ignition and sustaining a fire in such areas.
            
            ## Where does the data come from?
            The wind data was sourced from NASA's MERRA-2 data, which obtains data from various satellites. The data has a spatial resolution of 0.5 &deg; x 0.625 &deg; taken over hourly intervals.
            """)


def main():
    wind_page()



if __name__ == "__main__":
    main()
