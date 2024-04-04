import streamlit as st
from PIL import Image
from data_loader import load_fire_data, create_temperature_chart,create_humidity_chart,create_wind_chart, create_precipitation_chart, create_fire_occurence_chart

st.set_page_config(page_title="Climate Dashboard", layout="wide",initial_sidebar_state="expanded")
#-------------------------------------------------------------------

fire_all_data, fire_dataframes = load_fire_data()

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

def home_page_bak():
    # Add bristol logo and nasa logo
    col1, col2, col3 ,col4 = st.columns(4)
    with col1:
        st.write("")  # Empty column for spacing
    with col2:
        st.write("")  # Empty column for spacing
    with col3:
        university_logo = "./image/University_of_Bristol_logo.png"
        resized_university_logo = resize_image(university_logo, target_height=50)
        st.image(resized_university_logo)
    with col4:
        nasa_logo = "./image/NASA_logo.svg.png"
        resized_nasa_logo = resize_image(nasa_logo, target_height=50)
        st.image(resized_nasa_logo)
    st.header("Climate change dashboard")

    st.markdown("""
    Welcome to the California Wildfire and Climate Data Exploration Dashboard. 
      """)

    st.write("\n\n")

    st.markdown("""
    This comprehensive interactive tool enables users to delve into a wide range of environmental factors that affect the California region, including precipitation patterns, temperature variations, wind speed, and humidity levels. By integrating this data, the dashboard offers insights into how these diverse climate conditions can influence the frequency, intensity, and distribution of wildfires. Users can explore monthly and daily trends, compare different environmental factors side by side, and visualize the intricate relationships between climate variables and wildfire events at selected times. 
    Dive deep into the data to uncover patterns, correlations, and trends that can help in understanding the complex dynamics of wildfires in California.
     """)

    factor_descriptions = {
    "Humidity": {
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart shows fluctuations in specific humidity over time, which can affect cloud formation and precipitation patterns, contributing to climate change impacts."
    },
    "Precipitation": {
        "data_source": "NASA - IMERG",
        "trend_description": "The chart displays monthly total precipitation, revealing changes in precipitation patterns that could lead to more extreme weather events like droughts and floods due to climate change."
    },
    "Temperature": {
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart illustrates the upward trend in average surface temperature over time, a direct consequence of climate change, which can cause sea level rise, melting glaciers, and ecosystem disruptions."
    },
    "Fire Occurence": {
        "data_source": "NASA - xxx",
        "trend_description": "The chart shows the frequency of wildfires occurring each month, highlighting the increasing risk and occurrence of wildfires due to hotter temperatures and drier conditions caused by climate change."
    },
    "Wind":{
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart shows the wind speed over time. The fluctuating pattern of the line indicates seasonal variations in wind speed, with peaks and troughs occurring annually. "
    }
    }

    charts = {
        "Humidity": create_humidity_chart,
        "Precipitation": create_precipitation_chart,
        "Temperature": create_temperature_chart,
        "Fire Occurence": create_fire_occurence_chart,
        "Wind": create_wind_chart
    }
    # mini chart
    factors = list(charts.keys())
    num_factors = len(factors)
    num_rows = (num_factors + 1) // 2

    for row in range(num_rows):
        cols = st.columns(2)

        for col_idx, col in enumerate(cols):
            factor_idx = row * 2 + col_idx
            if factor_idx < num_factors:
                factor = factors[factor_idx]
                with col:
                    with st.spinner(f'Loading {factor} chart...'):
                        # Call the chart function to get the figure
                        fig = charts[factor]()
                        st.plotly_chart(fig, use_container_width=True)

                with col:
                    factor_page_link = f"pages/{factor.lower()}.py"
                    st.page_link(page=factor_page_link, label=f"**Go to {factor} details**", icon="🏠")
                    st.write(f"**Data Source:** {factor_descriptions[factor]['data_source']}")
                    st.write(f"**Trend Description:** {factor_descriptions[factor]['trend_description']}")


def home_page():
    # Add bristol logo and nasa logo
    col1, col2, col3 ,col4 = st.columns(4)
    with col1:
        st.write("")  # Empty column for spacing
    with col2:
        st.write("")  # Empty column for spacing
    with col3:
        university_logo = "./image/University_of_Bristol_logo.png"
        resized_university_logo = resize_image(university_logo, target_height=50)
        st.image(resized_university_logo)
    with col4:
        nasa_logo = "./image/NASA_logo.svg.png"
        resized_nasa_logo = resize_image(nasa_logo, target_height=50)
        st.image(resized_nasa_logo)
    st.header("Climate change dashboard")

    st.markdown("""
    Welcome to the California Wildfire and Climate Data Exploration Dashboard.  
    This comprehensive interactive tool enables users to delve into a wide range of environmental factors that affect the California region, including precipitation patterns, temperature variations, wind speed, and humidity levels. By integrating this data, the dashboard offers insights into how these diverse climate conditions can influence the frequency, intensity, and distribution of wildfires. Users can explore monthly or daily data and trends, compare different environmental factors side by side, and visualize the intricate relationships between climate variables and wildfire events at selected times.
    Dive deep into the data to uncover patterns, correlations, and trends that can help in understanding the complex dynamics of wildfires in California.
     """)

    factor_descriptions = {
    "Humidity": {
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart shows fluctuations in specific humidity over time, which can affect cloud formation and precipitation patterns, contributing to climate change impacts."
    },
    "Precipitation": {
        "data_source": "NASA - IMERG",
        "trend_description": "The chart displays monthly total precipitation, revealing changes in precipitation patterns that could lead to more extreme weather events like droughts and floods due to climate change."
    },
    "Temperature": {
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart illustrates the upward trend in average surface temperature over time, a direct consequence of climate change, which can cause sea level rise, melting glaciers, and ecosystem disruptions."
    },
    "Fire Occurence": {
        "data_source": "NASA - xxx",
        "trend_description": "The chart shows the frequency of wildfires occurring each month, highlighting the increasing risk and occurrence of wildfires due to hotter temperatures and drier conditions caused by climate change."
    },
    "Wind":{
        "data_source": "NASA - MERRA-2",
        "trend_description": "The chart shows the wind speed over time. The fluctuating pattern of the line indicates seasonal variations in wind speed, with peaks and troughs occurring annually. "
    }
    }

    charts = {
        "Humidity": create_humidity_chart,
        "Precipitation": create_precipitation_chart,
        "Temperature": create_temperature_chart,
        "Fire Occurence": create_fire_occurence_chart,
        "Wind": create_wind_chart
    }

    st.subheader("Climate Factors")
    factors = ["Humidity", "Precipitation", "Temperature", "Wind"]
    num_factors = len(factors)
    num_rows = (num_factors + 1) // 2

    for row in range(num_rows):
        cols = st.columns(2)

        for col_idx, col in enumerate(cols):
            factor_idx = row * 2 + col_idx
            if factor_idx < num_factors:
                factor = factors[factor_idx]
                with col:
                    with st.spinner(f'Loading {factor} chart...'):
                        # Call the chart function to get the figure
                        fig = charts[factor]()
                        st.plotly_chart(fig, use_container_width=True)

                with col:
                    factor_page_link = f"pages/{factor.lower()}.py"
                    st.page_link(page=factor_page_link, label=f"Go to {factor} details", icon="🏠")
                    st.write(f"**Data Source:** {factor_descriptions[factor]['data_source']}")
                    st.write(f"**Trend Description:** {factor_descriptions[factor]['trend_description']}")
    # Add space between two section
    st.write("\n\n\n")
    st.subheader("Fire Data Analysis")
    col_fire, col_mul = st.columns(2)
    with col_fire:
        factor_fire = "Fire Occurence"
        #st.subheader('Fire Occurence')
        st.write("**Fire Occurence**")
        fig = charts[factor_fire]()
    with col_fire:
        st.plotly_chart(fig, use_container_width=True)
        factor_page_link = f"pages/{factor_fire.lower()}.py"
        st.page_link(page=factor_page_link, label=f"Go to {factor_fire} details", icon="🏠")
        st.write(f"**Trend Description:** {factor_descriptions[factor_fire]['trend_description']}")
    with col_mul:
        st.write("**Multivariable Visualisation**")
        st.image('./image/Multivariable_visualisation_thumbnail2.png', use_column_width=True)
    with col_mul:
        st.page_link(page="pages/Multivariable graph.py", label=f"Go to Multivariable Visualisation page", icon="🏠")
        st.write(f"**Description:** This interface allows users to interactively explore various climate-related factors over a geographical area. Users can select a date to display data points on a map, with the color and size of each point.")

    # Add space between two section
    st.write("\n\n\n")
    st.subheader("Predictive Insights")
    st.write("Using machine learning to predict high-risk areas for future wildfires.")
    st.page_link(page="pages/Predictive Model.py", label=f"Go to Predictive Model page", icon="🏠")

    # Clean cache
    # This is due to the fact that the cache doesn't recognise the addition of files within a folder.
    # so I've included a temporary shortcut to clear the cache here.
    # If you upload a new data file, click that button to clear the cache.
    st.write("\n\n\n")
    st.write("\n\n\n")
    st.write("\n\n\n")
    st.write("\n\n\n")
    st.write("\n\n\n")
    st.write("\n\n\n")
    st.markdown("""
     It‘s a temporary shortcut to clear the cache here.
     If you upload a new data file, click that button to clear the cache.
       """)
    if st.button('Clear Cache'):
        st.caching.clear_cache()
        st.success('Cache cleared! Please rerun the app.')

def main():

    st.sidebar.header("About")
    st.sidebar.info(
        """
        This dashboard presents a visual analysis of climate-related data such as temperature, precipitation, 
        humidity, wind speed, and wildfire occurrences. All data is sourced from NASA.
        """
    )
    home_page()
if __name__ == "__main__":

    main()


