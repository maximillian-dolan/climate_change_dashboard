

import streamlit as st

def Learn_More_page():
    # Add a title to the page
    st.title('Learn More')

    # Add a header for data source information
    st.header('Data Source Information')

    # Add a subheader for the source (e.g., NASA Earth Data)
    st.subheader('By NASA Earth Data')

    # Add rows for satellite information
    cols = st.columns(2)

    # Add information about each satellite to respective row
    with cols[0]:
        st.subheader("Fire Data")
        st.write("""
        MODIS collects global data across 36 spectral channels every 1 to 2 days. It's useful for monitoring fires, natural hazards, and oil spills.
        
        For more information and access to MODIS data, visit [NASA's MODIS Earth DATA](https://www.earthdata.nasa.gov/sensors/modis)
        """)

        st.subheader("IMERG")
        st.write(""" 
        IMERG, an advanced algorithm by NASA, estimates global precipitation using satellite data, particularly in areas without ground-based instruments. It merges data from TRMM (2000-2015) and GPM (2014-present) satellites, creating a continuous dataset for over two decades. This data enables analysis of precipitation trends, improving climate models and understanding extreme weather events. IMERG provides near real-time updates every half-hour, supporting applications in disaster management, disease control, resource planning, and food security globally.
        
        For more information and access to IMERG Data, visit [NASA's Global Precipitation Measurement](https://gpm.nasa.gov/data/imerg)
        """)

    with cols[1]:
        st.subheader("MERRA-2")
        st.write("""
        MERRA-2 is a significant resource for comprehending Earth's climate system and its evolution. It offers data on weather, atmosphere, hydrology, and ecology. Researchers utilize it to analyze climate trends, air quality, water resources, ecosystem dynamics, and extreme weather. Moreover, MERRA-2 aids in validating and refining climate models, thus improving future climate projections. In essence, MERRA-2 plays a vital role in tackling climate-related issues and guiding decision-making. It is used for Temperature, Wind and Humidity Data.
        
        For more information and access to MERRA-2 Data,visit the [NASA's Global Modeling and Assimilation Office](https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/)
        """)

        st.subheader("AQUA")
        st.write("""
        The Aqua satellite mission, launched by NASA in 2002, collects extensive data on various aspects of Earth's water cycle and atmospheric conditions, including aerosols. Equipped with six Earth-observing instruments, Aqua provides valuable information on aerosol concentrations, which are crucial for understanding air quality, climate change, and environmental health. 
        By measuring aerosols along with other variables like water vapor, clouds, and precipitation, Aqua enables researchers to analyze aerosol distribution, composition, and their impact on climate dynamics. This data is instrumental for studying atmospheric processes, assessing pollution levels, and monitoring changes in air quality over time. 
        Therefore, Aqua's comprehensive dataset plays a vital role in advancing aerosol analysis and enhancing our understanding of Earth's atmospheric composition and its implications for the environment and human health. It is used for Aerosol data
        
        For more information and access to AQUA Data, visit the [NASA's AQUA Project Science](https://aqua.nasa.gov/)
        """)

def main():
    Learn_More_page()
    
    # Add spacing between satellite information and footer
    st.markdown("<br>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style='background-color: #0099cc; padding: 20px; border-radius: 5px; font-size: 10px;'>
            <p>University of Bristol, School of Chemistry, Cantock’s Close, Bristol, BS8 1TS</p>
            <p><a href="https://sites.google.com/view/httpscontactus/home" style='color: white;'>Contact Us</a> | <a href="https://sites.google.com/view/httpsuserworkinggroup/home" style='color: white;'>User working Group</a> | <a href="https://sites.google.com/view/httpswhoweare/home" style='color: white;'>Who We Are</a> | <a href="https://sites.google.com/view/httpsfaqs/home" style='color: white;'>FAQ</a> | <a href="https://forms.gle/zvU9SuKtmfeD89U48" style='color: white;'>Help us improve our dashboard</a></p>
            <p style="margin-top: 10px;">Follow Us: <a href="https://github.com/maximillian-dolan/climate_change_dashboard"><img src="https://www.1kosmos.com/wp-content/uploads/2021/07/GitHub-logo.png" width="60px"></a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Call the function to run the Streamlit app
if __name__ == "__main__":
    main()
