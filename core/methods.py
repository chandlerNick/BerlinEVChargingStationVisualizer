import pandas as pd
import geopandas as gpd
import core.HelperTools as ht

import folium
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from core.demand_methods.DemandMethods import robert_demands
from core.suggestions_methods.SuggestionsMethods import initialize_file, load_suggestions, save_suggestions, SUGGESTIONS_FILE



# -----------------------------------------------------------------------

def sort_by_plz_add_geometry(dfr, dfg, pdict):
    '''
    Inputs:
        - dfr: 
        - dfg: 
        - pdict:
    Outputs: 
    Postconditions: None
    '''
    dframe = dfr.copy()
    df_geo_input = dfg.copy()
    
    sorted_df = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2 = sorted_df.merge(df_geo_input, on=pdict["geocode"], how='left')
    sorted_df3 = sorted_df2.dropna(subset=['geometry'])
    
    sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')
    
    return ret


# -----------------------------------------------------------------------------


@ht.timer
def preprop_lstat(dfr, dfg, paramdict):
    """
    Preprocesses DataFrame for Electric Charging Stations and Geographic Information
    Inputs: dfr - DataFrame with charging station data; dfg - DataFrame with geographic data; pdict - parameter dictionary
    Outputs: Processed and sorted DataFrame
    Postconditions: DataFrame is filtered for Berlin, reformatted, and merged with geographic data
    """

    df_register_input = dfr.copy()
    df_geo_input = dfg.copy()
    
    df_register_input = df_register_input.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    df_register_input.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

    # Convert to string
    df_register_input['Breitengrad'] = df_register_input['Breitengrad'].astype(str)
    df_register_input['Längengrad'] = df_register_input['Längengrad'].astype(str)

    # Now replace the commas with periods
    df_register_input['Breitengrad'] = df_register_input['Breitengrad'].str.replace(',', '.')
    df_register_input['Längengrad'] = df_register_input['Längengrad'].str.replace(',', '.')

    df_register_input = df_register_input[(df_register_input["Bundesland"] == 'Berlin') & 
                      (df_register_input["PLZ"] > 10115) &  
                      (df_register_input["PLZ"] < 14200)]
        
    return sort_by_plz_add_geometry(df_register_input, df_geo_input, paramdict)


# -----------------------------------------------------------------------------


@ht.timer
def count_plz_occurrences(df_charging_stations_preprocessed):
    """
    Counts Loading Stations Per Postal Code
    Inputs: df_lstat2 - DataFrame with charging station data and geometry
    Outputs: DataFrame with counts and first geometry per postal code
    Postconditions: DataFrame is grouped by postal code with counts and geometry aggregated
    """

    df_charging_stations_counts = df_charging_stations_preprocessed.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return df_charging_stations_counts


# -----------------------------------------------------------------------------


@ht.timer
def preprop_resid(dfr, dfg, paramdict):
    """
    Preprocesses DataFrame for Residents and Geographic Information
    Inputs: dfr - DataFrame with postal codes, population, and coordinates; dfg - DataFrame with geographic data; paramdict - parameter dictionary
    Outputs: Processed and sorted DataFrame
    Postconditions: DataFrame is filtered, reformatted, and merged with geographic data
    """

    df_register_input = dfr.copy()
    df_geo_input = dfg.copy()    
    
    df_register_input = df_register_input.loc[:, ['plz', 'einwohner', 'lat', 'lon']]
    df_register_input.rename(columns={"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace=True)

    # Convert to string
    df_register_input['Breitengrad'] = df_register_input['Breitengrad'].astype(str)
    df_register_input['Längengrad'] = df_register_input['Längengrad'].astype(str)

    # Now replace the commas with periods
    df_register_input['Breitengrad'] = df_register_input['Breitengrad'].str.replace(',', '.')
    df_register_input['Längengrad'] = df_register_input['Längengrad'].str.replace(',', '.')

    df_register_input = df_register_input[ 
                      (df_register_input["PLZ"] > 10000) &  
                      (df_register_input["PLZ"] < 14200)]
        
    return sort_by_plz_add_geometry(df_register_input, df_geo_input, paramdict)


# -----------------------------------------------------------------------------


@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """
    Makes Streamlit App with Heatmap of Electric Charging Stations and Residents
    Inputs: 
        - dfr1: 
        - dfr2: 
    Outputs: None
    Postconditions: Streamlit app is built and deployed
    """
    
    dframe1 = dfr1.copy()
    df_register_input = dfr2.copy()

    # Merge resident and charging station data
    dframe1['PLZ'] = dframe1['PLZ'].astype(int)
    dframe1 = dframe1.iloc[:, 0:2]
    merged = df_register_input.merge(dframe1, on='PLZ', how='left')

    # Fill NaN values with 0
    merged['Number'] = merged['Number'].fillna(0)

    # Streamlit app
    st.title('Heatmaps: Electric Charging Stations and Residents')

    # Create a radio button for layer selection
    layer_selection = st.radio("Select Layer", ("Residents", "Charging Stations", "Demand"))

    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        
        # Create a color map for Residents using LinearColormap from branca
        color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=df_register_input['Einwohner'].min(), vmax=df_register_input['Einwohner'].max())

        # Add polygons to the map for Residents
        for idx, row in df_register_input.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Einwohner']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
            ).add_to(m)

    elif layer_selection == "Demand":
        # Implement Demand
        merged['Demand'] = robert_demands(merged['Number'], merged['Einwohner'])
        
        # Create colormap for demand
        mi = merged['Demand'].min()
        ma = merged['Demand'].max()
        color_map = LinearColormap(
            colors=["darkblue", "darkblue", "blue", "blue", "lightblue", "lightblue", "red", "red"], 
            vmin=mi, 
            vmax=ma
        )
        color_map = color_map.scale(vmin=mi, vmax=ma)

        # Add polygons to the map for Demand
        for idx, row in merged.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Demand']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Demand: {row['Demand']}"
            ).add_to(m)
    
    else:
        # Create a color map for Numbers
        color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red', 'magenta'], vmin=dframe1['Number'].min(), vmax=dframe1['Number'].max())

        # Add polygons to the map for Numbers
        for idx, row in merged.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Number']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}"
            ).add_to(m)

    # Add color map to the map
    color_map.add_to(m)
    
    folium_static(m, width=800, height=600)
    
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Suggestions section
    # ---------------------------------------------------------------------------------------------------------------------
    
    # Call the init file method (creates the file if it doesn't yet exist)
    initialize_file()
    
    # Load suggestions into memory
    if "suggestions" not in st.session_state:
        st.session_state["suggestions"] = load_suggestions()

    # Sidebar menu
    option = st.sidebar.radio("Choose an option:", ["Submit a Suggestion", "View Suggestions"])

    if option == "Submit a Suggestion":
        st.header("Submit Your Suggestion")
        
        # Text input for the suggestion
        suggestion = st.text_area("Write your suggestion here:")
        
        # Button to submit the suggestion
        if st.button("Submit Suggestion"):
            if suggestion.strip():  # Check if the suggestion is not empty
                st.session_state["suggestions"].append(suggestion.strip())
                save_suggestions(st.session_state["suggestions"])  # Save to file
                st.success("Thank you for your suggestion!")
            else:
                st.warning("Suggestion cannot be empty.")

    elif option == "View Suggestions":
        st.header("Suggestions List")
        
        if st.session_state["suggestions"]:
            # Display each suggestion
            for i, suggestion in enumerate(st.session_state["suggestions"], 1):
                st.write(f"{i}. {suggestion}")
        else:
            st.info("No suggestions have been submitted yet.")

