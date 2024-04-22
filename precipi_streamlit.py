import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from joblib import load
from sklearn.preprocessing import scale, StandardScaler

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
    fire_dataframes[f'{year}'] = whole_fire_df

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

#-------------------------------------------------------------------
# Import Temperature data

temp_folder_path = './temperature_data/processed'
csv_temp_files = [file for file in os.listdir(temp_folder_path) if file.endswith('.csv')]

temp_dataframes = {}
for csv_file in csv_temp_files:

    date = csv_file.split('.')[0]
        
    temp_df = pd.read_csv(os.path.join(temp_folder_path, csv_file))
    temp_df.dropna(inplace = True) # Drops all points not within California
    temp_df['temperature'] = temp_df['AvgSurfT_tavg'] - 273.15 # Convert from kelvin to celsius
    temp_dataframes[f'{date}'] = temp_df

temp_all_data = pd.concat(temp_dataframes, ignore_index=True)

#--------------------------------------------------------------------
# Import precipitation data (for multivariable plot)

# set the folder path of csv file
precipitation_folder_path_mv = './precipitation_data/.csv/daily'

# get the list of files
precipitation_file_pattern_mv = '%Y-%m-%d'
precipitation_file_paths_mv = [os.path.join(precipitation_folder_path_mv, f) for f in os.listdir(precipitation_folder_path_mv) if
                  f.endswith('.csv') and datetime.strptime(f.split('.')[0], precipitation_file_pattern_mv)]

# Get the list of dates
precipitation_dates_mv = [os.path.splitext(f)[0] for f in os.listdir(precipitation_folder_path_mv) if f.endswith('.csv')]
#precipitation_dates_mv = [datetime.strptime(date, precipitation_file_pattern_mv) for date in precipitation_dates_mv]
precipitation_dates_mv.sort()

#--------------------------------------------------------------------
# Import humidity data (for multivariable plot)

humidity_folder_path_mv = "./humidity_data/processed_data"

# get list of dates 
humidity_dates_mv = [datetime.strptime(os.path.splitext(f)[0], '%Y-%m-%d') for f in os.listdir(humidity_folder_path_mv) if f.endswith('.csv')]
humidity_dates_mv.sort()

#-------------------------------------------------------------------
# Import Wind data

wind_folder_path = './wind_data/wind_data/csv/daily'
csv_wind_files = [file for file in os.listdir(wind_folder_path) if file.endswith('.csv')]

wind_dataframes = {}
for csv_file in csv_wind_files:

    date = csv_file.split('.')[0]
        
    wind_df = pd.read_csv(os.path.join(wind_folder_path, csv_file))
    wind_df = wind_df[wind_df['SPEEDLML'] != 0] # Drops all points not within California
    wind_df['wind_speed'] = wind_df['SPEEDLML'] 
    wind_dataframes[f'{date}'] = wind_df

wind_all_data = pd.concat(wind_dataframes, ignore_index=True)
#--------------------------------------------------------------------
# Adjusting the image size
def resize_image(image_path, target_height):
    image = Image.open(image_path)
    width, height = image.size
    aspect_ratio = width / height
    new_width = int(aspect_ratio * target_height)
    resized_image = image.resize((new_width, target_height))
    return resized_image
#--------------------------------------------------------------------
# Create pages

def home_page():
    # Add bristol logo and nasa logo
    col1, col2, col3 = st.columns(3)
    with col1:
        university_logo = "./image/bristol.png"
        resized_university_logo = resize_image(university_logo, target_height=50)
        st.image(resized_university_logo)
    with col3:
        st.write("")  # Empty column for spacing
    with col2:
        nasa_logo = "./image/NASA.png"
        resized_nasa_logo = resize_image(nasa_logo, target_height=50)
        st.image(resized_nasa_logo)
    st.header("Climate change dashboard")
    st.write("Description of the dashboard...")
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'

    st.markdown("""Welcome to the California Wildfire and Climate Data Exploration Dashboard. This comprehensive interactive tool enables users to delve into a wide range of environmental factors that affect the California region, including precipitation patterns, temperature variations, wind speed, and humidity levels. By integrating this data, the dashboard offers insights into how these diverse climate conditions can influence the frequency, intensity, and distribution of wildfires. Users can explore monthly and daily trends, compare different environmental factors side by side, and visualize the intricate relationships between climate variables and wildfire events at selected times. Dive deep into the data to uncover patterns, correlations, and trends that can help in understanding the complex dynamics of wildfires in California.
    """)
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'

    factor_descriptions = {
    "Humidity": {
        "data_source": "NASA -",
        "trend_description": "The chart shows fluctuations in specific humidity over time, which can affect cloud formation and precipitation patterns, contributing to climate change impacts."
    },
    "Precipitation": {
        "data_source": "NASA -",
        "trend_description": "The chart displays monthly total precipitation, revealing changes in precipitation patterns that could lead to more extreme weather events like droughts and floods due to climate change."
    },
    "Temperature": {
        "data_source": "NASA -",
        "trend_description": "The chart illustrates the upward trend in average surface temperature over time, a direct consequence of climate change, which can cause sea level rise, melting glaciers, and ecosystem disruptions."
    },
    "Fire Occurence": {
        "data_source": "NASA -",
        "trend_description": "The chart shows the frequency of wildfires occurring each month, highlighting the increasing risk and occurrence of wildfires due to hotter temperatures and drier conditions caused by climate change."
    }
    }

    def create_precipitation_chart():
        precipitation_file_path = "precipitation_data/.csv/monthly_precipitation_summary.csv"
        precipitation_df = pd.read_csv(precipitation_file_path)
        fig = px.line(precipitation_df, x='Month', y='Total Precipitation', title='Monthly Total Precipitation')
        return fig

    def create_humidity_chart():
        humidity_data_path = './humidity_data/processed_data'
        all_humidity_files = os.listdir(humidity_data_path)
        dayly_humidity_sums = {}
        for file_name in all_humidity_files:
            try:
                year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
            except ValueError:
                continue  # Skip files that don't match the date format
            file_path = os.path.join(humidity_data_path, file_name)
            humidity_df = pd.read_csv(file_path)
            # Sum humidity for the month
            date_key = year_month_day.strftime("%Y-%m-%d")
            dayly_humidity_sums[date_key] = dayly_humidity_sums.get(date_key, 0) + humidity_df[
                'Qair_f_inst'].sum()
        # Create DataFrame for daily humidity sums
        df_total_humidity_per_day = pd.DataFrame(list(dayly_humidity_sums.items()),
                                              columns=['Date', 'Specific Humidity(kg/kg)'])
        # create line graph
        fig = px.line(df_total_humidity_per_day, x='Date', y='Specific Humidity(kg/kg)', title='Total Specific Humidity over Time')
        return fig
    
    def create_temperature_chart():
        temperature_data_path = './temperature_data/processed'
        all_temperature_files = os.listdir(temperature_data_path)
        dayly_temperature_sums = {}

        for file_name in all_temperature_files:
            try:
                year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
            except ValueError:
                continue  # Skip files that don't match the date format
            file_path = os.path.join(temperature_data_path, file_name)
            temperature_df = pd.read_csv(file_path)
            # Sum humidity for the month
            date_key = year_month_day.strftime("%Y-%m-%d")
            dayly_temperature_sums[date_key] = dayly_temperature_sums.get(date_key, 0) + temperature_df[
                'AvgSurfT_tavg'].sum()
        # Create DataFrame for daily humidity sums
        df_total_humidity_per_day = pd.DataFrame(list(dayly_temperature_sums.items()),
                                              columns=['Date', 'AvgSurfT_tavg'])
        # create line graph
        fig = px.line(df_total_humidity_per_day, x='Date', y='AvgSurfT_tavg', title='Total Temperature over Time')
        return fig

    def create_fire_occurence_chart():
        # Calculate the count of fires per month for each year
        firecount_dataframes = {}

        for df in fire_dataframes:
            specific_month_counts = pd.DataFrame(data=fire_dataframes[df].value_counts(subset='month', sort=False))
            specific_month_counts['month names'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                                    'August', 'September', 'October', 'November', 'December']
            specific_month_counts['year'] = df
            specific_month_counts['count'] = specific_month_counts['count'] / len(fire_dataframes[df])

            firecount_dataframes[df] = specific_month_counts

        all_fire_frequencies = pd.concat(firecount_dataframes, ignore_index=True)
        fire_frequency_chart = px.bar(data_frame=all_fire_frequencies,
                                      x='month names',
                                      y='count',
                                      hover_name='month names',
                                      animation_frame='year',
                                      animation_group='month names',
                                      range_y=[0, 0.7],
                                      color_discrete_sequence=['red'] * len(all_fire_frequencies))
        return fire_frequency_chart
    charts = {
        "Humidity": create_humidity_chart,
        "Precipitation": create_precipitation_chart,
        "Temperature": create_temperature_chart,
        "Fire Occurence": create_fire_occurence_chart
    }
    # Save current page
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'home'

    # mini chart
    for index, (factor, chart_func) in enumerate(charts.items()):
        col1, col2 = st.columns([3, 1])

        with col1:
            # Call the chart function to get the figure
            fig = chart_func()
            st.plotly_chart(fig)


        with col2:
            factor_page_link = f"pages/{factor.lower()}.py"
            st.page_link(page=factor_page_link, label=f"Go to {factor} details", icon="🏠")
            # Rerun the app to move to the selected factor's page
            #st.experimental_rerun()
            #st.page_link(f"{factor}.py", label=f"{factor}", icon="🏠")
        with st.container():
            st.write(f"**Data Source:** {factor_descriptions[factor]['data_source']}")
            st.write(f"**Trend Description:** {factor_descriptions[factor]['trend_description']}")
    #Just for debug
    st.write('Current page in session state:', st.session_state['current_page'])

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


def precipitation_page():
    st.header("Precipitation Data")
    st.write("Explore Precipitation Data.")
    st.markdown("""
        ## Why is Precipitation Data Important?
        Precipitation is a key natural phenomenon essential for agriculture, water resource management, and the prevention of natural disasters. In California, variations in precipitation patterns are crucial for understanding and preventing natural disasters like forest fires. Prolonged droughts or insufficient rainfall lead to dry vegetation, increasing the risk and intensity of wildfires. Conversely, adequate rainfall helps maintain vegetation moisture, reducing the occurrence of fires.

        ## How Does Precipitation Influence Wildfires?
        The rainy season in California plays a critical role in the ecological cycle, promoting vigorous vegetation growth that enriches the ecosystem. However, this abundance of growth also leads to an accumulation of potential fuel for wildfires. Post-rainy season, dead and decaying vegetation can dry out rapidly under the hot, arid conditions typical of California's climate, significantly increasing the risk of wildfires. This paradox highlights the complex relationship between precipitation, vegetation growth, and wildfire dynamics, underscoring the importance of integrated climate and wildfire management strategies.
        """)
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
    show_fires = st.checkbox(label = 'Show Fire data')

    # set the folder path of csv file
    base_directory = "./precipitation_data"
    precipitation_folder_path = f'./{base_directory}/.csv/{precipitation_data_type}'

    # get the list of file
    precipitation_file_pattern = '%Y-%m-%d' if precipitation_data_type == 'daily' else '%Y-%m'
    precipitation_file_paths = [os.path.join(precipitation_folder_path, f) for f in os.listdir(precipitation_folder_path) if
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
            precipitation_color_scale_max = precipitation_df['precipitationCal' if precipitation_data_type == 'daily' else 'precipitation'].quantile(
                precipitation_confidence_level)

            # Create map

            fig_precipitation = px.density_mapbox(
                precipitation_df,
                lat='lat',
                lon='lon',
                z='precipitationCal' if precipitation_data_type == 'daily' else 'precipitation',
                radius=10,
                color_continuous_scale=px.colors.sequential.Viridis,
                mapbox_style='open-street-map',
                zoom=4,
                title=f'Precipitation Heatmap for {date_str}'
            )

            # create fire plot                  
 
            if show_fires == True:
                fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == str(selected_date)[:10]] if precipitation_data_type == 'daily' else fire_dataframe[fire_dataframe['month'] == str(selected_date)[5:7]]
                fig_precipitation.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                lat='latitude',
                                                lon='longitude',
                                                color_discrete_sequence=['red']*len(fire_dataframe_date),
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

            """
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
"""
def temperature_page():
    st.header("Temperature Data")
    st.write('Explore temperature data.')

    # Create daily average dataframe
    temp_daily_average = pd.DataFrame(data = {'date':sorted(temp_dataframes.keys(), key=lambda x:x.lower()), 'average temperature':np.zeros(len(temp_dataframes))})

    for index, row in temp_daily_average.iterrows():
        temp_df = temp_dataframes[temp_daily_average['date'][index]]
        temp_daily_average['average temperature'][index] = np.mean(temp_df['temperature'])


    # Create page tabs
    tab1,tab2,tab3 = st.tabs(['chart','stats','information'])

    with tab1:
        # Choose date to display
        selected_date_temp = st.select_slider('Select a date', options=sorted(temp_dataframes.keys(), key=lambda x:x.lower()),key='fire_date_slider')
        
        # checkbox to show fires  
        show_fires = st.checkbox(label = 'Show Fire data')

        fire_dataframe = fire_dataframes['2015'] # For now only 2015 temp data is used. If more data added, this will need to be changed
        
        # Create map  
        fig_temperature = px.scatter_mapbox( temp_dataframes[selected_date_temp],
                    lat='lat',
                    lon='lon',
                    #size='temperature',
                    #z = 'temperature',
                    color='temperature',
                    color_continuous_scale=px.colors.sequential.thermal,
                    range_color=(min(temp_all_data['temperature']), max(temp_all_data['temperature'])),
                    mapbox_style='open-street-map',
                    zoom=3.7,
                    title=f'temperature for {2015}'
                    )
        
        # Add fire data 
        if show_fires == True:
            fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == selected_date_temp]
            fig_temperature.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                        lat='latitude',
                                                        lon='longitude',
                                                        color_discrete_sequence=['red']*len(fire_dataframe_date),
                                                        mapbox_style='open-street-map',
                                                        zoom=4,
                                                        title=f'Fire locations'  
                                                        ).data[0]
                                    )

        st.plotly_chart(fig_temperature)
   
    with tab2:
        temp_line = px.line(temp_daily_average, x='date', y='average temperature')
        temp_line.update_layout(yaxis_title='average temperature (celsius)', xaxis_title = '')
        st.plotly_chart(temp_line)

    with tab3:
        st.markdown("""
        ## Why is Temperature Data Important?
        Temperature is a key component of fire weather conditions. High temperatures can increase the likelihood and intensity of wildfires by drying out vegetation, making it more susceptible to ignition and rapid spread. Understanding temperature patterns helps forecasters and firefighters anticipate periods of heightened fire danger.
        """)


def fire_page():
    st.header("Fire Occurence Data")
    st.write("data and visualizations")

    #Create tabs for two plots
    tab1, tab2, tab3 = st.tabs(['locations','frequency', 'information'])

    #Create fire locations plot
    with tab1:

        fire_data_type = st.radio('select data type',('monthly','yearly'))

        if fire_data_type == 'monthly':
            fire_year = st.select_slider('year', options = sorted(fire_dataframes.keys(), key=lambda x:x.lower()))
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
    
    with tab3:
        st.markdown("""
                    
        ## Why do we track wildfires?
        Tracking Wildfire ocurrence is not only important actively for locating and fighting fire, but archiving the data helps to identify trends and at-risk areas. It also serves as a demonstration as to how climate change is affecting them.
                    
        """)

        
def wind_page():
    st.header("Wind Data")
    st.write('Explore wind data.')

    # Choose date to display
    selected_date_wind = st.select_slider('Select a date', options=sorted(wind_dataframes.keys(), key=lambda x:x.lower()),key='fire_date_slider')

    
    # checkbox to show fires  
    show_fires = st.checkbox(label = 'Show Fire data')

    fire_dataframe = fire_dataframes['2015'] # For now only 2015 temp data is used. If more data added, this will need to be changed
    
    # Create map  
    fig_wind = px.scatter_mapbox( wind_dataframes[selected_date_wind],
                lat='lat',
                lon='lon',
                color='wind_speed',
                color_continuous_scale=px.colors.sequential.Viridis,
                range_color=(min(wind_all_data['wind_speed']), max(wind_all_data['wind_speed'])),
                mapbox_style='open-street-map',
                zoom=3.7,
                title=f'Average wind speed for {2015}'
                )
    
    # Add fire data 
    if show_fires == True:
        fire_dataframe_date = fire_dataframe[fire_dataframe['acq_date'] == selected_date_wind]
        fig_wind.add_trace(px.scatter_mapbox(fire_dataframe_date,
                                                    lat='latitude',
                                                    lon='longitude',
                                                    color_discrete_sequence=['red']*len(fire_dataframe_date),
                                                    mapbox_style='open-street-map',
                                                    zoom=4,
                                                    title=f'Fire locations'  
                                                    ).data[0]
                                 )

    st.plotly_chart(fig_wind)


def parse_julian_date(date_str):
    year = int(date_str[1:5])
    day_of_year = int(date_str[5:8])
    return datetime(year, 1, 1) + pd.to_timedelta(day_of_year - 1, unit='d')

def aerosol_page():
    st.header("Aerosol Optical Depth Data")
    st.write("Explore Aerosol Optical Depth Data across California.")

    tab1, tab2 = st.tabs(['plot', 'Information'])

    with tab1:
        aerosol_folder_path = "./Aerosol_data/processed_data"
        
        aerosol_dates = sorted(
            [parse_julian_date(f.split('.')[1]) for f in os.listdir(aerosol_folder_path) if f.startswith('aerosol_data_MYD04_3K')]
        )

        selected_date = st.select_slider(
            'Select a date',
            options=aerosol_dates,
            format_func=lambda date: date.strftime('%Y-%m-%d')
        )

        california_geojson = gpd.read_file('Aerosol_data/california.geojson')  

        if selected_date:
            date_str = selected_date.strftime('%Y-%m-%d')
            aerosol_file_path = None
            for filename in os.listdir(aerosol_folder_path):
                file_date = parse_julian_date(filename.split('.')[1])
                if file_date == selected_date:
                    aerosol_file_path = os.path.join(aerosol_folder_path, filename)
                    break

            if aerosol_file_path and os.path.exists(aerosol_file_path):
                df = pd.read_csv(aerosol_file_path)

                # Clean data: Replace negative and -9999 values
                df['Optical_Depth_Land_And_Ocean'] = df['Optical_Depth_Land_And_Ocean'].replace(-9999.0, np.nan)
                df['Optical_Depth_Land_And_Ocean'] = df['Optical_Depth_Land_And_Ocean'].apply(lambda x: max(x, 0.1) if not pd.isna(x) else np.nan)
                df.dropna(subset=['Optical_Depth_Land_And_Ocean'], inplace=True)

                # Filter data within California boundaries
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
                gdf = gdf[gdf.geometry.within(california_geojson.unary_union)]

                if not gdf.empty:
                    optical_depth_max = gdf['Optical_Depth_Land_And_Ocean'].quantile(0.95)
                    optical_depth_min = gdf['Optical_Depth_Land_And_Ocean'].min()

                    fig_aerosol = px.scatter_mapbox(
                        gdf,
                        lat='Latitude',
                        lon='Longitude',
                        size='Optical_Depth_Land_And_Ocean',
                        color='Optical_Depth_Land_And_Ocean',
                        color_continuous_scale=px.colors.sequential.Viridis,
                        labels={'Optical_Depth_Land_And_Ocean': 'Aerosol Depth'},
                        size_max=15,
                        range_color=(optical_depth_min, optical_depth_max),
                        mapbox_style='open-street-map',
                        zoom=4,
                        title=f'Aerosol Optical Depth for {date_str}'
                    )
                    st.plotly_chart(fig_aerosol)
                else:
                    st.error("No valid data available for the selected date. Please try another date.")
            else:
                st.error("File not found. Please check the file path or availability.")

    with tab2:
        st.markdown("""
            ## Why is Aerosol data Important?
            """)



def multivariable_graph():
    
    st.header('Multivariable visualisation')

    # Create slider
    date_mv = st.select_slider('Select a date', options=sorted(temp_dataframes.keys(), key=lambda x:x.lower()), key='mv_slider')

    data_options = []
    col1, col2 = st.columns([0.75,0.25])

    # Add precipitation dataframe
    precipitation_file_path_mv = os.path.join(precipitation_folder_path_mv, f"{date_mv}.csv")
    if os.path.exists(precipitation_file_path_mv):
        precipitation_df_mv = pd.read_csv(precipitation_file_path_mv)
        lon_to_longitude(precipitation_df_mv)
        precipitation_df_mv['precipitation'] = precipitation_df_mv['precipitationCal']
        precipitation_df_mv = precipitation_df_mv[['latitude','longitude','precipitation']]
        precipitation_df_mv = mv_rounder(precipitation_df_mv,'precipitation')

        data_options.append('precipitation')


    # Add wind speed dataframe
    wind_file_path_mv = os.path.join(wind_folder_path, f"{date_mv}.csv")
    if os.path.exists(wind_file_path_mv):
        wind_df_mv = pd.read_csv(wind_file_path_mv)
        lon_to_longitude(wind_df_mv)
        wind_df_mv = wind_df_mv[wind_df_mv['SPEEDLML'] != 0]
        wind_df_mv['wind_speed'] = wind_df_mv['SPEEDLML']
        wind_df_mv = wind_df_mv[['latitude','longitude','wind_speed']]
        wind_df_mv = mv_rounder(wind_df_mv,'wind_speed')

        data_options.append('wind_speed')

    # Add humidity dataframe
    humidity_file_path_mv= os.path.join(humidity_folder_path_mv, f"{date_mv}.csv")
    if os.path.exists(humidity_file_path_mv):
        humidity_df_mv = pd.read_csv(humidity_file_path_mv)
        lon_to_longitude(humidity_df_mv)
        humidity_df_mv = humidity_df_mv[humidity_df_mv['Qair_f_inst'] != 0]
        humidity_df_mv['humidity'] = humidity_df_mv['Qair_f_inst']
        humidity_df_mv = humidity_df_mv[['latitude','longitude','humidity']]
        humidity_df_mv = mv_rounder(humidity_df_mv,'humidity')

        data_options.append('humidity')
        
    # Add temperature dataframe
    if date_mv in temp_dataframes:
        temp_df_mv = temp_dataframes[date_mv]
        lon_to_longitude(temp_df_mv)
        temp_df_mv = temp_df_mv[['latitude','longitude','temperature']]
        temp_df_mv = mv_rounder(temp_df_mv,'temperature')

        data_options.append('temperature')

    # Add fire dataframe
    if date_mv[:4] in fire_dataframes:
        fire_df_mv = fire_dataframes[date_mv[:4]]
        fire_df_mv = fire_df_mv[fire_df_mv['acq_date'] == date_mv]
        with col2:
            show_fires_mv = st.checkbox(label = 'Show Fire data')   
            
    else:
        show_fires_mv = False
    
    # Merge dataframes into one dataframe
    df_total_mv = pd.merge(humidity_df_mv, temp_df_mv, on=['latitude', 'longitude'])
    if os.path.exists(precipitation_file_path_mv): #temporary fix for glitch in which data isnt there for precipitation 2010
        df_total_mv = pd.merge(df_total_mv,precipitation_df_mv, on=['latitude', 'longitude'])
    df_total_mv = pd.merge(df_total_mv,wind_df_mv, on=['latitude', 'longitude'])

    with col2:
        color_mv = st.selectbox(label = 'Color', options = data_options)
        size_mv = st.selectbox(label = 'Size', options = data_options)

    multivariable_fig = px.scatter_mapbox(df_total_mv,
                                            lat='latitude',
                                            lon='longitude',
                                            size=size_mv,
                                            hover_name = size_mv,
                                            color=color_mv,
                                            color_continuous_scale=px.colors.sequential.thermal,
                                            #range_color=(min(temp_all_data['temperature']), max(temp_all_data['temperature'])),
                                            mapbox_style='open-street-map',
                                            zoom=3.7,
                                            width = 500)
    
        # Add fire data 
    if show_fires_mv == True:
        multivariable_fig.add_trace(px.scatter_mapbox(fire_df_mv,
                                                    lat='latitude',
                                                    lon='longitude',
                                                    color_discrete_sequence=['red']*len(fire_df_mv),
                                                    mapbox_style='open-street-map',
                                                    zoom=4,
                                                    title=f'Fire locations'  
                                                    ).data[0])
    with col1:
        st.plotly_chart(multivariable_fig)

def predictive():
    
    st.header('Predictive chart')

    # Stupid way to do it but for now is the only way to only have dates that have all date for currently 
    august_2015 = ['2015-08-01', '2015-08-02', '2015-08-03', '2015-08-04', '2015-08-05', '2015-08-06', '2015-08-07', '2015-08-08', '2015-08-09', '2015-08-10', '2015-08-11', '2015-08-12', '2015-08-13', '2015-08-14', '2015-08-15', '2015-08-16', '2015-08-17', '2015-08-18', '2015-08-19', '2015-08-20', '2015-08-21', '2015-08-22', '2015-08-23', '2015-08-24', '2015-08-25', '2015-08-26', '2015-08-27', '2015-08-28', '2015-08-29', '2015-08-30', '2015-08-31']

    # Create slider
    date_predictive = st.select_slider('Select a date', options=august_2015, key='predictive_slider')
    #list(set(temp_dataframes.keys()).intersection(precipitation_dates_predictive)

    data_options = []
    col1, col2 = st.columns([0.75,0.25])

    with col2:
        predictor_type = st.radio(label = 'Which predictive model to use', options = ['Random Forest', 'Special Vector Machine'])
    
    # Import classifier
    if predictor_type == 'Random Forest':
        classifier = load('rf_biased.joblib')
    elif predictor_type == 'Special Vector Machine':
        classifier = load('svc_biased.joblib')
    #classifier = load('rf_classifier.joblib')

    # Add precipitation dataframe
    precipitation_file_path_predictive = os.path.join(precipitation_folder_path_mv, f"{date_predictive}.csv")
    if os.path.exists(precipitation_file_path_predictive):
        precipitation_df_predictive = pd.read_csv(precipitation_file_path_predictive)
        lon_to_longitude(precipitation_df_predictive)
        precipitation_df_predictive['precipitation'] = precipitation_df_predictive['precipitationCal']
        precipitation_df_predictive = precipitation_df_predictive[['latitude','longitude','precipitation']]
        precipitation_df_predictive = mv_rounder(precipitation_df_predictive,'precipitation')

        data_options.append('precipitation')


    # Add wind speed dataframe
    wind_file_path_predictive = os.path.join(wind_folder_path, f"{date_predictive}.csv")
    if os.path.exists(wind_file_path_predictive):
        wind_df_predictive = pd.read_csv(wind_file_path_predictive)
        lon_to_longitude(wind_df_predictive)
        wind_df_predictive = wind_df_predictive[wind_df_predictive['SPEEDLML'] != 0]
        wind_df_predictive['wind_speed'] = wind_df_predictive['SPEEDLML']
        wind_df_predictive = wind_df_predictive[['latitude','longitude','wind_speed']]
        wind_df_predictive = mv_rounder(wind_df_predictive,'wind_speed')

        data_options.append('wind_speed')

    # Add humidity dataframe
    humidity_file_path_predictive= os.path.join(humidity_folder_path_mv, f"{date_predictive}.csv")
    if os.path.exists(humidity_file_path_predictive):
        humidity_df_predictive = pd.read_csv(humidity_file_path_predictive)
        lon_to_longitude(humidity_df_predictive)
        humidity_df_predictive = humidity_df_predictive[humidity_df_predictive['Qair_f_inst'] != 0]
        humidity_df_predictive['humidity'] = humidity_df_predictive['Qair_f_inst']
        humidity_df_predictive = humidity_df_predictive[['latitude','longitude','humidity']]
        humidity_df_predictive = mv_rounder(humidity_df_predictive,'humidity')

        data_options.append('humidity')
        
    # Add temperature dataframe
    if date_predictive in temp_dataframes:
        temp_df_predictive = temp_dataframes[date_predictive]
        lon_to_longitude(temp_df_predictive)
        temp_df_predictive = temp_df_predictive[['latitude','longitude','temperature']]
        temp_df_predictive = mv_rounder(temp_df_predictive,'temperature')

        data_options.append('temperature')

    # Add fire dataframe
    if date_predictive[:4] in fire_dataframes:
        fire_df_predictive = fire_dataframes[date_predictive[:4]]
        fire_df_predictive = fire_df_predictive[fire_df_predictive['acq_date'] == date_predictive]
        with col2:
            show_fires_predictive = st.checkbox(label = 'Show Fire data') 
            
    else:
        show_fires_predictive = False
    
    # Merge dataframes into one dataframe
    df_total_predictive = pd.merge(humidity_df_predictive, temp_df_predictive, on=['latitude', 'longitude'])
    if os.path.exists(precipitation_file_path_predictive): #temporary fix for glitch in which data isnt there for precipitation 2010
        df_total_predictive = pd.merge(df_total_predictive,precipitation_df_predictive, on=['latitude', 'longitude'])
    df_total_predictive = pd.merge(df_total_predictive,wind_df_predictive, on=['latitude', 'longitude'])

    data = df_total_predictive[['humidity','temperature','precipitation','wind_speed']]
    df_total_predictive['fire_prediction'] = classifier.predict(StandardScaler().fit_transform(data))
    df_total_predictive[['probability_0','probability_1']] = classifier.predict_proba(StandardScaler().fit_transform(data))

    predictive_fig = px.scatter_mapbox(df_total_predictive,
                                            lat='latitude',
                                            lon='longitude',
                                            size='probability_1',
                                            hover_name = 'probability_1',
                                            color_discrete_sequence=['orange']*len(df_total_predictive),
                                            mapbox_style='open-street-map',
                                            zoom=3.7,
                                            width = 500)
    
    # Add fire data 
    if show_fires_predictive == True:
        predictive_fig.add_trace(px.scatter_mapbox(fire_df_predictive,
                                                    lat='latitude',
                                                    lon='longitude',
                                                    color_discrete_sequence=['red']*len(fire_df_predictive),
                                                    mapbox_style='open-street-map',
                                                    zoom=4,
                                                    title=f'Fire locations'  
                                                    ).data[0])
    with col1:
        st.plotly_chart(predictive_fig)
        #st.write(temp_dataframescs.keys())
        #st.write(precip_dates)
        #st.write(df_total_predictive[df_total_predictive['probability_1']>0.1])
        #st.write(df_total_predictive)


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
        "Temperature": temperature_page,
        "Wind Speed": wind_page,
        "Fire Occurence": fire_page,
        "Multivariable graph" : multivariable_graph,
        "Predictive Model": predictive,
        "Aerosol": aerosol_page
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


