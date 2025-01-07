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
    df_geo = dfg.copy()
    
    sorted_df = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2 = sorted_df.merge(df_geo, on=pdict["geocode"], how='left')
    sorted_df3 = sorted_df2.dropna(subset=['geometry'])
    
    sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')
    
    return ret


# -----------------------------------------------------------------------------


@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()
    
    dframe2 = dframe.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

    # Convert to string
    dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad'] = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad'] = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad'] = dframe2['Längengrad'].str.replace(',', '.')

    dframe3 = dframe2[(dframe2["Bundesland"] == 'Berlin') & 
                      (dframe2["PLZ"] > 10115) &  
                      (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret


# -----------------------------------------------------------------------------


@ht.timer
def count_plz_occurrences(df_lstat2):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df


# -----------------------------------------------------------------------------


@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()    
    
    dframe2 = dframe.loc[:, ['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns={"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace=True)

    # Convert to string
    dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad'] = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad'] = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad'] = dframe2['Längengrad'].str.replace(',', '.')

    dframe3 = dframe2[ 
                      (dframe2["PLZ"] > 10000) &  
                      (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret


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
    dframe2 = dfr2.copy()

    # Merge resident and charging station data
    dframe1['PLZ'] = dframe1['PLZ'].astype(int)
    dframe1 = dframe1.iloc[:, 0:2]
    merged = dframe2.merge(dframe1, on='PLZ', how='left')

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
        color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=dframe2['Einwohner'].min(), vmax=dframe2['Einwohner'].max())

        # Add polygons to the map for Residents
        for idx, row in dframe2.iterrows():
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

