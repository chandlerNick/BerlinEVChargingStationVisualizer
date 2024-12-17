# BerlinEVChargingStationVisualizer
This repo houses a streamlit app that visualizes the distribution of EV charging stations and population by PLZ (postal code)

https://berlinevdistributiongeovisualizer.streamlit.app/

Google Doc: https://docs.google.com/document/d/1Nufz29A0aTRTqbKYzp88Gdk-rSo3kfsH87DRXjxQvao/edit?usp=sharing

#### Code Documentation

Program:

    In the main function, we load in the datasets, do transformations, and eventually pass them to a streamlit runner function.

    Note that in each of the following functions, 
    - dfg, is the geography dataframe that gives the coordinates on the map to draw the polygons which inscribe each PLZ
    - dfr, is a dataframe that changes based on the function
    - pdict, contains parameters used in each of the functions
    - dfr1, dfr2, are dataframes with the EV charging information and population information respectively, as well as the relevant geographic information

    A breakdown of each function in methods.py is as follows:
    - sort_by_plz_add_geometry(dfr, dfg, pdict)
    - preprop_lstat(dfr, dfg, pdict)
        - Preprocessing dataframe from Ladesaeulenregister.csv
        - Processes the charging station dataframe and returns the cleaned dataframe
    - count_plz_occurrences(df_lstat2)
        - Counts charging stations per PLZ
    - preprop_resid(dfr, dfg, pdict)
        - Preprocessing dataframe from plz_einwohner.csv
        - Processes the population dataframe
    - make_streamlit_electric_Charging_resid(dfr1, dfr2)
        - Makes Streamlit App with Heatmap of Electric Charging Stations and Residents

Interpretation of Results:
    
    The resulting program is a streamlit app that has a map of Berlin, subdivided by Postleitzahlen (PLZ).
    Each zone defined by the PLZ is given a color based on a gradient at the top of the map, with darker colors indicating a higher count of whichever variable is measured at that time by the overlay.
    Finally, there is functionality to switch between an overlay that displays the population by PLZ or the number of EV charging stations by PLZ. 


#### Analysis of Geovisualization

Question: Where do you see demand for additional electric charging stations?

Answer:

Assuming we define demand as the ratio of population over number of charging stations with a high value indicating a high demand for charging stations, we can make the following quick deductions from the visualization:

High demand PLZ were identified by looking at PLZ with a light yellow on the charging station map and medium lightness orange or darker on the population map, indicating few charging stations (<5) and medium to high population (>15000) respectively.
Based on this creterion, PLZ with a high demand for EV stations are:
- 12559
- 13589
- 13439
- 13407
- 13059
- 13627
- 13351
- 13349
- 13359
- 13189
- 10318
- 14193
- 12277
- 12307

