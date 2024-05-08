import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Import wind chart
from data_loader import create_humidity_chart
# Import fire data
from data_loader import load_fire_data
fire_all_data, fire_dataframes = load_fire_data()

st.set_page_config(layout="centered")

# Function to load fire data for a given date
def load_fire_data(selected_date, fire_folder_path='./USA_fire_date_2010_2023'):
    selected_year = str(selected_date.year)
    fire_file_path = os.path.join(fire_folder_path, f'fire_{selected_year}.csv')

    if os.path.exists(fire_file_path):
        fire_df = pd.read_csv(fire_file_path)
        fire_df['acq_date'] = pd.to_datetime(fire_df['acq_date'])
        return fire_df[fire_df['acq_date'] == selected_date]
    else:
        return pd.DataFrame()


def humidity_page():
    st.header("Humidity Data")
    st.write("Explore Humidity Data")


    tab1, tab2, tab3 = st.tabs(['Plot', 'Scatter graph', 'Information'])
    with tab1:
        humidity_data_type = st.radio("Select Data Type", ('Daily',))

        # Checkbox to show fires
        show_fires = st.checkbox(label='Show Fire Data')

        # Set the folder path of csv file to point directly to the processed data
        humidity_folder_path = "./humidity_data/processed_data"

        # Get the list of dates from the file names
        humidity_dates = [
            datetime.strptime(f.split('.')[0], '%Y-%m-%d') for f in os.listdir(humidity_folder_path) if
            f.endswith('.csv')
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
            date_str = selected_date.strftime('%Y-%m-%d')
            humidity_file_path = os.path.join(humidity_folder_path, f"{date_str}.csv")

            if os.path.exists(humidity_file_path):
                # Read csv file
                humidity_df = pd.read_csv(humidity_file_path)
                humidity_df.rename(columns={'Qair_f_inst': 'Humidity (kg/kg)'}, inplace=True)

                # Set the confidence level
                humidity_confidence_level = 0.95
                humidity_color_scale_max = humidity_df['Humidity (kg/kg)'].quantile(humidity_confidence_level)

                # Create map
                fig_humidity = px.scatter_mapbox(
                    humidity_df,
                    lat='lat',
                    lon='lon',
                    size='Humidity (kg/kg)',
                    color='Humidity (kg/kg)',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    range_color=(humidity_df['Humidity (kg/kg)'].min(), humidity_color_scale_max),
                    mapbox_style='open-street-map',
                    zoom=3.7,
                    title=f'Humidity for {date_str}'
                )

            if show_fires:
                fire_df = load_fire_data(selected_date)
                selected_year = str(selected_date)[:4]
                if selected_year in fire_dataframes:
                    fire_dataframe_date = fire_dataframes[selected_year][
                        fire_dataframes[selected_year]['acq_date'] == str(selected_date)[:10]]
                    if not fire_dataframe_date.empty:
                        fig_humidity.add_trace(px.scatter_mapbox(
                            fire_dataframe_date,
                            lat='latitude',
                            lon='longitude',
                            color_discrete_sequence=['red'] * len(fire_dataframe_date),
                            mapbox_style='open-street-map',
                            zoom=4,
                            title='Fire locations'
                        ).data[0])
                    else:
                        st.warning(f"No fire on {date_str}.")

            # Show the plot
            st.plotly_chart(fig_humidity)
            # Download button
            # Check file exists
            if os.path.exists(humidity_file_path):
                # Read file
                with open(humidity_file_path, "rb") as file:
                    btn = st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=f"{date_str}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("File not found.")
    with tab2:
        fig_humidity_chart = create_humidity_chart()
        st.plotly_chart(fig_humidity_chart, use_container_width=True)
    with tab3:
        st.markdown("""
            ## Why is Humidity Data Important?
            The minimum daily relative humidity plays a significant role in the occurrence of wildfires. This is because humidity levels directly affect the moisture content of vegetation. Higher humidity levels lead to an increase in the moisture content of fuels, which makes them less likely to ignite and burn. On the other hand, lower humidity levels cause vegetation to dry out, increasing the risk of fire ignition. Additionally, low humidity levels can intensify the spread of fires and make them spread faster. Humidity also interacts with temperature and wind to affect overall weather conditions, which in turn impacts fire behavior.

            ## Where does the data come from?
            The humidity data was sourced from NASA's MERRA-2 data, which obtains data from various satellites. The data has a spatial resolution of 0.5 &deg; x 0.625 &deg; taken over hourly intervals.
            """)


# Main layout of the app
def main():
    humidity_page()


if __name__ == "__main__":
    main()

