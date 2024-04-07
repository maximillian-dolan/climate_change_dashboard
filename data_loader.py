import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from joblib import load
#from sklearn.preprocessing import scale, StandardScaler


#-------------------------------------------------------------------
# Importing fire data
@st.cache_data(show_spinner=False)
def load_fire_data():
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
    return fire_all_data, fire_dataframes
#-------------------------------------------------------------------
# Import Temperature data
@st.cache_data(show_spinner=False)
def load_and_process_temperature_data():
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
    return temp_all_data, temp_dataframes
#--------------------------------------------------------------------
# Import precipitation data (for multivariable plot)
@st.cache_data(show_spinner=False)
def load_and_process_precipitation_data():
    precipitation_base_directory_mv = "./precipitation_data"
    precipitation_folder_path_mv = f'./{precipitation_base_directory_mv}/.csv/daily'

    # get the list of files
    precipitation_file_pattern_mv = '%Y-%m-%d'
    precipitation_file_paths_mv = [os.path.join(precipitation_folder_path_mv, f) for f in
                                   os.listdir(precipitation_folder_path_mv) if
                                   f.endswith('.csv') and datetime.strptime(f.split('.')[0],
                                                                            precipitation_file_pattern_mv)]

    # Get the list of dates
    precipitation_dates_mv = [os.path.splitext(f)[0] for f in os.listdir(precipitation_folder_path_mv) if
                              f.endswith('.csv')]
    # precipitation_dates_mv = [datetime.strptime(date, precipitation_file_pattern_mv) for date in precipitation_dates_mv]

    precipitation_dates_mv.sort()
    return precipitation_dates_mv
#--------------------------------------------------------------------
# Import humidity data (for multivariable plot)
@st.cache_data(show_spinner=False)
def load_and_process_humidity_data():
    humidity_folder_path_mv = "./humidity_data/processed_data"

    # get list of dates
    humidity_dates_mv = [datetime.strptime(os.path.splitext(f)[0], '%Y-%m-%d') for f in os.listdir(humidity_folder_path_mv) if f.endswith('.csv')]
    humidity_dates_mv.sort()
    return humidity_dates_mv

# -------------------------------------------------------------------
# Import Wind data
@st.cache_data(show_spinner=False)
def load_and_process_wind_data():
    wind_folder_path = './wind_data/wind_data/csv/daily'
    csv_wind_files = [file for file in os.listdir(wind_folder_path) if file.endswith('.csv')]

    wind_dataframes = {}
    for csv_file in csv_wind_files:
        date = csv_file.split('.')[0]

        wind_df = pd.read_csv(os.path.join(wind_folder_path, csv_file))
        wind_df = wind_df[wind_df['SPEEDLML'] != 0]  # Drops all points not within California
        wind_df['wind_speed'] = wind_df['SPEEDLML']
        wind_dataframes[f'{date}'] = wind_df

    wind_all_data = pd.concat(wind_dataframes, ignore_index=True)
    return wind_all_data, wind_dataframes,wind_folder_path
#--------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def find_common_dates_from_datasets():
    # Define path
    wind_folder_path = './wind_data/wind_data/csv/daily'
    temp_folder_path = './temperature_data/processed'
    humidity_folder_path = "./humidity_data/processed_data"
    precipitation_folder_path = './precipitation_data/.csv/daily'
    # Get date
    wind_dates = set(f.split('.')[0] for f in os.listdir(wind_folder_path) if f.endswith('.csv'))
    temp_dates = set(f.split('.')[0] for f in os.listdir(temp_folder_path) if f.endswith('.csv'))
    humidity_dates = set(f.split('.')[0] for f in os.listdir(humidity_folder_path) if f.endswith('.csv'))
    precipitation_dates = set(f.split('.')[0] for f in os.listdir(precipitation_folder_path) if f.endswith('.csv'))
    # Common dates
    common_dates = sorted(wind_dates & temp_dates & humidity_dates & precipitation_dates)
    return common_dates
#--------------------------------------------------------------------
# Generate chart
@st.cache_data(show_spinner=False)
def create_precipitation_chart():
    precipitation_file_path = "precipitation_data/.csv/monthly_precipitation_summary.csv"
    precipitation_df = pd.read_csv(precipitation_file_path)
    fig = px.line(precipitation_df, x='Month', y='Total Precipitation', title='Monthly Total Precipitation')
    return fig

@st.cache_data(show_spinner=False)
def create_humidity_chart_bak():
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
    fig = px.line(df_total_humidity_per_day, x='Date', y='Specific Humidity(kg/kg)', title='Specific Humidity')
    return fig

@st.cache_data(show_spinner=False)
def create_humidity_chart():
    humidity_data_path = './humidity_data/processed_data'
    all_humidity_files = os.listdir(humidity_data_path)
    daily_humidities = {}

    for file_name in all_humidity_files:
        try:
            year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
        except ValueError:
            continue  # Skip files that don't match the date format
        file_path = os.path.join(humidity_data_path, file_name)
        humidity_df = pd.read_csv(file_path)

        # Collect daily humidities
        date_key = year_month_day.strftime("%Y-%m-%d")
        if date_key not in daily_humidities:
            daily_humidities[date_key] = []
        daily_humidities[date_key].extend(humidity_df['Qair_f_inst'].tolist())

    # Calculate average humidity for each day
    daily_average_humidities = {date: sum(humids) / len(humids) for date, humids in daily_humidities.items()}

    # Create DataFrame for daily average humidities
    df_daily_average_humidity = pd.DataFrame(list(daily_average_humidities.items()),
                                             columns=['Date', 'Specific Humidity(kg/kg)'])

    # Set the window size for the moving average, here assumed to be 30 days.
    window_size = 30
    # Calculate the moving average.
    df_daily_average_humidity['Moving_Avg'] = df_daily_average_humidity['Specific Humidity(kg/kg)'].rolling(
        window=window_size).mean()

    # Chart
    fig = px.scatter(df_daily_average_humidity, x='Date', y='Moving_Avg',
                  title='Average Specific Humidity')
    return fig
@st.cache_data(show_spinner=False)
def create_temperature_chart_average():
    temperature_data_path = './temperature_data/processed'
    all_temperature_files = os.listdir(temperature_data_path)
    daily_temperatures = {}

    for file_name in all_temperature_files:
        try:
            year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
            file_path = os.path.join(temperature_data_path, file_name)
            temperature_df = pd.read_csv(file_path)

            # Collect daily temperatures
            date_key = year_month_day.strftime("%Y-%m-%d")
            if date_key not in daily_temperatures:
                daily_temperatures[date_key] = []
            daily_temperatures[date_key].extend(temperature_df['AvgSurfT_tavg'].tolist())
        except ValueError:
            continue  # Skip files that don't match the date format
        except pd.errors.EmptyDataError:
            print(f"Warning: Skipping empty or invalid file {file_name}")
            continue

    # Calculate average temperature for each day
    daily_average_temperatures = {date: sum(temps) / len(temps) for date, temps in daily_temperatures.items()}

    # Create DataFrame for daily average temperatures
    df_daily_average_temperature = pd.DataFrame(list(daily_average_temperatures.items()),
                                                columns=['Date', 'AvgSurfT_tavg'])

    # Sort DataFrame by Date to ensure the line graph is chronological
    df_daily_average_temperature['Date'] = pd.to_datetime(df_daily_average_temperature['Date'])
    df_daily_average_temperature.sort_values('Date', inplace=True)


    # Create line graph
    fig = px.line(df_daily_average_temperature, x='Date', y='AvgSurfT_tavg',
                  title='Daily Average Temperature over Time')
    return fig

@st.cache_data(show_spinner=False)
def create_temperature_chart():
    temperature_data_path = './temperature_data/processed'
    all_temperature_files = os.listdir(temperature_data_path)
    daily_temperatures = {}

    for file_name in all_temperature_files:
        try:
            year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
            file_path = os.path.join(temperature_data_path, file_name)
            temperature_df = pd.read_csv(file_path)

            # Collect daily temperatures
            date_key = year_month_day.strftime("%Y-%m-%d")
            if date_key not in daily_temperatures:
                daily_temperatures[date_key] = []
            daily_temperatures[date_key].extend(temperature_df['AvgSurfT_tavg'].tolist())
        except ValueError:
            continue  # Skip files that don't match the date format
        except pd.errors.EmptyDataError:
            print(f"Warning: Skipping empty or invalid file {file_name}")
            continue

    # Calculate average temperature for each day
    daily_average_temperatures = {date: sum(temps) / len(temps) for date, temps in daily_temperatures.items()}

    # Create DataFrame for daily average temperatures
    df_daily_average_temperature = pd.DataFrame(list(daily_average_temperatures.items()),
                                                columns=['Date', 'AvgSurfT_tavg'])
    # Set the window size for the moving average, here assumed to be 30 days.
    window_size = 30
    # Calculate the moving average.
    df_daily_average_temperature['Moving_Avg'] = df_daily_average_temperature['AvgSurfT_tavg'].rolling(
        window=window_size).mean()
    # Chart
    fig = px.scatter(df_daily_average_temperature, x='Date', y='Moving_Avg',
                  title='Average Temperature')
    return fig

@st.cache_data(show_spinner=False)
def create_fire_occurence_chart():
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
        fire_df['confidence'] = fire_df['confidence'] / 100
        fire_df['year'] = fire_df['year'].apply(str)

    fire_all_data = pd.concat(fire_dataframes, ignore_index=True)
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

@st.cache_data(show_spinner=False)
def create_wind_chart():
    wind_data_path = './wind_data/wind_data/csv/daily'
    all_wind_files = os.listdir(wind_data_path)
    daily_winds = {}
    for file_name in all_wind_files:
        try:
            year_month_day = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d")
            file_path = os.path.join(wind_data_path, file_name)
            wind_df = pd.read_csv(file_path)

            # Collect daily wind speeds
            date_key = year_month_day.strftime("%Y-%m-%d")
            if date_key not in daily_winds:
                daily_winds[date_key] = []
            daily_winds[date_key].extend(wind_df['SPEEDLML'].tolist())
        except ValueError:
            continue  # Skip files that don't match the date format
        except pd.errors.EmptyDataError:
            print(f"Warning: Skipping empty or invalid file {file_name}")
            continue

    # Calculate average wind speed for each day
    daily_average_winds = {date: sum(speeds) / len(speeds) for date, speeds in daily_winds.items() if speeds}

    # Create DataFrame for daily average wind speeds
    df_daily_average_wind = pd.DataFrame(list(daily_average_winds.items()), columns=['Date', 'AverageWindSpeed'])

    # Convert 'Date' to datetime and sort DataFrame by Date to ensure the line graph is chronological
    df_daily_average_wind['Date'] = pd.to_datetime(df_daily_average_wind['Date'])
    df_daily_average_wind.sort_values('Date', inplace=True)

    # Set the window size for the moving average, here assumed to be 30 days.
    window_size = 30
    # Calculate the moving average for wind speed
    df_daily_average_wind['Moving_Avg'] = df_daily_average_wind['AverageWindSpeed'].rolling(
        window=window_size).mean()

    # Create line graph for the moving average of wind speed
    fig = px.line(df_daily_average_wind, x='Date', y='Moving_Avg',
                  title='Average Wind Speed')
    return fig




