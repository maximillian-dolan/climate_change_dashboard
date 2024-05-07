import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

from data_loader import load_fire_data
fire_all_data, fire_dataframes = load_fire_data()

st.set_page_config(layout="centered")
def precipitation_page():
    st.header("Precipitation Data")
    st.write("Explore Precipitation Data.")

    # Create tabs for two plots
    tab1, tab2, tab3 = st.tabs(['Plot', 'Line graph', 'Information'])
    with tab1:
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
                                    f.endswith('.csv') and datetime.strptime(f.split('.')[0],
                                                                             precipitation_file_pattern)]

        # Get the list of date
        precipitation_dates = [os.path.splitext(f)[0] for f in os.listdir(precipitation_folder_path) if
                               f.endswith('.csv')]
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
                precipitation_df.rename(columns={'precipitationCal': 'Precipitation (mm)'}, inplace=True)

                # set the confidence level
                precipitation_confidence_level = 0.95
                precipitation_color_scale_max = precipitation_df[
                    'Precipitation (mm)' if precipitation_data_type == 'daily' else 'precipitation'].quantile(
                    precipitation_confidence_level)

                # Create map
                fig_precipitation = px.density_mapbox(
                    precipitation_df,
                    lat='lat',
                    lon='lon',
                    z='Precipitation (mm)' if precipitation_data_type == 'daily' else 'precipitation',
                    radius=5,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    mapbox_style='open-street-map',
                    zoom=3.7,
                    title=f'Precipitation Heatmap for {date_str}'
                )

                # create fire plot

                if show_fires == True:
                    fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == str(selected_date)[
                                                                                       :10]] if precipitation_data_type == 'daily' else \
                    fire_dataframe[fire_dataframe['month'] == str(selected_date)[5:7]]
                    if not fire_dataframe_date.empty:
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
                    else:
                        st.warning(f"No fire data available for {date_str}.")
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

    with tab2:
        # Line graph
        st.header("Monthly Precipitation Trends")
        precipitation_file_path = "precipitation_data/.csv/monthly_precipitation_summary.csv"
        monthly_precipitation_df = pd.read_csv(precipitation_file_path)
        fig_monthly = px.line(monthly_precipitation_df, x='Month', y='Total Precipitation')
        fig_monthly.update_layout(yaxis_title='Total Precipitation (mm)', xaxis_title='Month')
        st.plotly_chart(fig_monthly)

    with tab3:
        st.markdown("""
            ## Why is Precipitation Data Important?
            Precipitation is a key natural phenomenon essential for agriculture, water resource management, and the prevention of natural disasters. In California, variations in precipitation patterns are crucial for understanding and preventing natural disasters like forest fires. Prolonged droughts or insufficient rainfall lead to dry vegetation, increasing the risk and intensity of wildfires. Conversely, adequate rainfall helps maintain vegetation moisture, reducing the occurrence of fires.

            ## How Does Precipitation Influence Wildfires?
            The rainy season in California plays a critical role in the ecological cycle, promoting vigorous vegetation growth that enriches the ecosystem. However, this abundance of growth also leads to an accumulation of potential fuel for wildfires. Post-rainy season, dead and decaying vegetation can dry out rapidly under the hot, arid conditions typical of California's climate, significantly increasing the risk of wildfires. This paradox highlights the complex relationship between precipitation, vegetation growth, and wildfire dynamics, underscoring the importance of integrated climate and wildfire management strategies.

            ## where does the data from？
            NASA’s Integrated Multi-satellitE Retrievals for GPM (IMERG) algorithm combines information from the GPM satellite constellation to estimate precipitation over the majority of the Earth's surface. 
            """)


def main():
    precipitation_page()



if __name__ == "__main__":
    main()
