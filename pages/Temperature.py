import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# -------------------------------------------------------------------
# Importing fire data

# Import wind chart
from data_loader import create_temperature_chart
# Import fire data
from data_loader import load_fire_data
fire_all_data, fire_dataframes = load_fire_data()


# -------------------------------------------------------------------
@st.cache_data
def load_temperature_data_for_date(selected_date, temp_data_folder='./temperature_data/processed'):
    date_str = selected_date.strftime('%Y-%m-%d')
    temp_file_path = os.path.join(temp_data_folder, f"{date_str}.csv")

    if os.path.exists(temp_file_path):
        temp_df = pd.read_csv(temp_file_path)
        return temp_df
    else:
        return pd.DataFrame()


def temperature_page():
    st.header("Temperature Data")
    st.write('Explore temperature data.')

    # Set the folder path of csv files
    temp_data_folder = "./temperature_data/processed"

    # Get the list of dates from the file names
    temp_dates = [
        datetime.strptime(f.split('.')[0], '%Y-%m-%d') for f in os.listdir(temp_data_folder) if
        f.endswith('.csv')
    ]
    temp_dates.sort()
    #print(temp_dates)

    # Create page tabs
    tab1, tab2, tab3 = st.tabs(['Plot', 'Scatter graph', 'Information'])

    with tab1:
        # Choose date to display
        selected_date_temp = st.select_slider(
            'Select a date',
            options=temp_dates,
            format_func=lambda date: date.strftime('%Y-%m-%d'),
            key='temp_date_slider'
        )
        # filter by date slider and rough california boundaries
        selected_year = str(selected_date_temp)[:4]
        fire_dataframe = fire_dataframes[selected_year]

        # checkbox to show fires
        show_fires = st.checkbox(label='Show Fire data')

        # Load temperature data for selected date
        date_str = selected_date_temp.strftime('%Y-%m-%d')
        temp_file_path = os.path.join(temp_data_folder, f"{date_str}.csv")
        if os.path.exists(temp_file_path):
            temp_df_for_date = pd.read_csv(temp_file_path)
            temp_df_for_date.rename(columns={'AvgSurfT_tavg': 'Temperature (celsius)'}, inplace=True)

        # Create map
        fig_temperature = px.scatter_mapbox(
            temp_df_for_date,
            lat='lat',
            lon='lon',
            color='Temperature (celsius)',
            color_continuous_scale=px.colors.sequential.thermal,
            range_color=(temp_df_for_date['Temperature (celsius)'].min(), temp_df_for_date['Temperature (celsius)'].max()),
            mapbox_style='open-street-map',
            zoom=3.7,
            title=f'Temperature for {selected_date_temp.strftime("%Y")}'
        )

        # Add fire data
        if show_fires and not temp_df_for_date.empty:
            fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == selected_date_temp]
            if not fire_dataframe_date.empty:
                fig_temperature.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                            lat='latitude',
                                                            lon='longitude',
                                                            color_discrete_sequence=['red'] * len(fire_dataframe_date),
                                                            mapbox_style='open-street-map',
                                                            zoom=4,
                                                            title=f'Fire locations'
                                                            ).data[0]
                )
            else:
                st.warning(f"No fire data available for {date_str}.")
        st.plotly_chart(fig_temperature)
        if os.path.exists(temp_file_path):
            # Read file
            with open(temp_file_path, "rb") as file:
                btn = st.download_button(
                    label="Download CSV",
                    data=file,
                    file_name=f"{date_str}.csv",
                    mime="text/csv"
                )
        else:
            st.write("File not found.")

    with tab2:
        fig_temperature_chart = create_temperature_chart()
        st.plotly_chart(fig_temperature_chart, use_container_width=True)
    with tab3:
        st.markdown("""
        ## Why is Temperature Data Important?
        Temperature is a key component of fire weather conditions. High temperatures can increase the likelihood and intensity of wildfires by drying out vegetation, making it more susceptible to ignition and rapid spread. Understanding temperature patterns helps forecasters and firefighters anticipate periods of heightened fire danger.
        
        ## Where does the data come from?
        The temperature data was sourced from NASA's MERRA-2 data, which obtains data from various satellites. The data has a spatial resolution of 0.5 &deg; x 0.625 &deg; taken over hourly intervals.
        """)


def main():
    temperature_page()

if __name__ == "__main__":
     main()
