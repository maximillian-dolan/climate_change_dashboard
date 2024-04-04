# California Wildfire and Climate Data Dashboard

## Overview
This repository contains the code and data for the California Wildfire and Climate Data Exploration Dashboard. This dashboard allows users to interact with and visualize a wide range of environmental data related to the California region, including information on precipitation, temperature, wind speed, and humidity.

## Structure
The project is organized into the following directories and files:

- `USA_fire_date_2010_2023/`: Fire data from 2010 to 2023
- `humidity_data/`: Contains processed humidity data.
- `image/`: Logos and images used in the dashboard.
- `pages/`: Individual Streamlit pages.
- `precipitation_data/`: Contains processed humidity data.
- `temperature_data/`: Contains processed humidity data.
- `wind_data/`: Contains processed humidity data.
- `California_County_Boundaries.geojson`: California_County_Boundaries.
- `ML_dataframe.csv`: The machine learning data frame used for analysis.
- `environment_v1.0.yml`: The conda environment file with all required dependencies. （This one may still need updating）
- `data_loader.py`: Some Data Functions and Chart Functions.
 
## Usage
To run the dashboard locally, clone the repository and set up the environment using the provided `environment_v1.0.yml` file. After activating the environment, navigate to the root directory and run:
streamlit run Home.py

## Data source
- `California_County_Boundaries.geojson`: https://gis.data.ca.gov/datasets/8713ced9b78a4abb97dc130a691a8695/explore?location=36.894820%2C-119.002032%2C6.53
