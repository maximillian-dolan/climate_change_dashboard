# California Wildfire and Climate Data Dashboard

## Overview
This repository contains the code and data for the California Wildfire and Climate Data Exploration Dashboard. This dashboard allows users to interact with and visualize a wide range of environmental data related to the California region, including information on Aerosol, precipitation, temperature, wind speed, and humidity.

## Structure
The project is organized into the following directories and files:

- `USA_fire_date_2010_2023/`: Fire data from 2010 to 2023
- `image/`: Logos and images used in the dashboard.
- `pages/`: Individual Streamlit pages.
- `Aerosol_data/`: Contains processed Aerosol data.
- `humidity_data/`: Contains processed humidity data.
- `precipitation_data/`: Contains processed precipitation data.
- `temperature_data/`: Contains processed temperature data.
- `wind_data/`: Contains processed wind data.
- `processing_scripts/`: Contains processing scripts.
- `California_County_Boundaries.geojson`: California_County_Boundaries.
- `ML_dataframe.csv`: The machine learning data frame used for analysis.
- `environment_v1.0.yml`: The conda environment file with all required dependencies. （This one may still need updating）
- `data_loader.py`: Some Data Functions and Chart Functions.
- `requirements.txt`: List of dependencies used by streamlit deploy service.
 
## Usage
To run the dashboard locally: clone the repository, set up, and activate the environment using the provided `environment_v1.0.yml` file:
~~~
$ conda env create -f environment_v1.0.yml
$ conda activate new_env
~~~
After activating the environment, navigate to the root directory and run:
~~~
$ streamlit run Home.py
~~~

Or alternatively, access remotely [here](https://climatechangedashboard.streamlit.app)

## Data source
- `California_County_Boundaries.geojson`: https://gis.data.ca.gov/datasets/8713ced9b78a4abb97dc130a691a8695/explore?location=36.894820%2C-119.002032%2C6.53
