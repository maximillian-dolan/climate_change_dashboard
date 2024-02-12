import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

def home_page():
    st.header("Climate change dashboard")
    st.write("Description of the dashboard...")

def humidity_page():
    st.header("Humidity Data")
    st.write("Humidity data and visualizations go here...")
def precipitation_page():
    st.header("Precipitation Data")
    st.write("Explore precipitation data.")

    # daily or monthly data type
    data_type = st.radio("Select data type", ('daily', 'monthly'))

    # set the folder path of csv file
    folder_path = f'./csv/{data_type}'

    # get the list of file
    file_pattern = '%Y-%m-%d' if data_type == 'daily' else '%Y-%m'
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                  f.endswith('.csv') and datetime.strptime(f.split('.')[0], file_pattern)]

    # Get the list of date
    dates = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.csv')]
    dates = [datetime.strptime(date, file_pattern) for date in dates]
    dates.sort()

    # Create slider
    selected_date = st.select_slider(
        'Select a date',
        options=dates,
        format_func=lambda date: date.strftime('%Y-%m-%d' if data_type == 'daily' else '%Y-%m'),
    )

    # Select date
    if selected_date:
        # define date_str and file_path
        date_str = selected_date.strftime(file_pattern)
        file_path = os.path.join(folder_path, f"{date_str}.csv")

        if os.path.exists(file_path):
            # Read csv file
            daily_data = pd.read_csv(file_path)

            # set the confidence level
            confidence_level = 0.95
            color_scale_max = daily_data['precipitationCal' if data_type == 'daily' else 'precipitation'].quantile(
                confidence_level)

            # Create map
            fig = px.scatter_mapbox(
                daily_data,
                lat='lat',
                lon='lon',
                size='precipitationCal' if data_type == 'daily' else 'precipitation',
                color='precipitationCal' if data_type == 'daily' else 'precipitation',
                color_continuous_scale=px.colors.sequential.Viridis,
                range_color=(0, color_scale_max),
                mapbox_style='open-street-map',
                zoom=4,
                title=f'Precipitation for {date_str}'
            )

            # Show
            st.plotly_chart(fig)

def temperature_page():
    st.header("Temperature Data")
    st.write("data and visualizations")
# Main layout of the app
def main():


    add_selectbox = st.sidebar.selectbox(
        "How would you like to be contacted?",
        ("Email", "Home phone", "Mobile phone")
    )
    st.sidebar.title("Menu")


    # Menu items
    menu_items = {
        "Home": home_page,
        "Humidity": humidity_page,
        "Precipitation": precipitation_page,
        "Temperature": temperature_page
        # Add other pages here
    }

    # Sidebar for navigation
    selection = st.sidebar.radio("Go to", list(menu_items.keys()))

    # Display the selected page with the content
    page = menu_items[selection]
    page()  # Call the respective function
    st.sidebar.write('**About**:'
                     ' All the data from NASA and XXX'

                     )
if __name__ == "__main__":
    main()


