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
from core.suggestions_methods.SuggestionsMethods import initialize_file, load_suggestions, save_suggestions, clear_suggestions



# -----------------------------------------------------------------------

def sort_by_plz_add_geometry(df_register_input, df_geo_input, pdict):
    '''
    Inputs:
        - df_register_input: pandas dataframe containing auxilliary information about the districts of Berlin (eg. number of residents)
        - df_geo_input: pandas dataframe containing geographic information about the districts of Berlin
        - pdict: dictionary containing filenames
    Outputs: A single geopandas geodataframe with the plz sorted and the geopandas geometry added by PLZ
    Postconditions: None
    '''
    dframe = df_register_input.copy()
    df_geo = df_geo_input.copy()
    
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
def make_streamlit_electric_Charging_resid(df_charging_stations, df_population):
    """
    Makes Streamlit App with Heatmap of Electric Charging Stations and Residents
    Inputs: 
        - df_charging_stations: A geodataframe sorted by PLZ and containing information about the charging stations
        - df_population: A geodataframe sorted by PLZ and containing information about the population
    Outputs: None
    Postconditions: Streamlit app is built and deployed
    """
    
    df_charging_stations_copy = df_charging_stations.copy()
    df_population_copy = df_population.copy()

    # Merge resident and charging station data
    df_charging_stations_copy['PLZ'] = df_charging_stations_copy['PLZ'].astype(int)
    df_charging_stations_copy = df_charging_stations_copy.iloc[:, 0:2]
    df_merged = df_population_copy.merge(df_charging_stations_copy, on='PLZ', how='left')

    # Fill NaN values with 0
    df_merged['Number'] = df_merged['Number'].fillna(0)

    # Streamlit app
    st.title('Heatmaps: Electric Charging Stations and Residents')

    
    # --------------------------------------------------------------------
    # Map Section
    # --------------------------------------------------------------------


    # Create a radio button for layer selection
    layer_selection = st.radio("Select Layer", ("Residents", "Charging Stations", "Demand"))
    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        
        # Create a color map for Residents using LinearColormap from branca
        color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=df_population_copy['Einwohner'].min(), vmax=df_population_copy['Einwohner'].max())

        # Add polygons to the map for Residents
        for idx, row in df_population_copy.iterrows():
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
        df_merged['Demand'] = robert_demands(df_merged['Number'], df_merged['Einwohner'])
        
        # Create colormap for demand
        mininmum_demand = df_merged['Demand'].min()
        maximum_demand = df_merged['Demand'].max()
        color_map = LinearColormap(
            colors=["darkblue", "darkblue", "blue", "blue", "lightblue", "lightblue", "red", "red"], 
            vmin=mininmum_demand, 
            vmax=maximum_demand
        )
        color_map = color_map.scale(vmin=mininmum_demand, vmax=maximum_demand)

        # Add polygons to the map for Demand
        for idx, row in df_merged.iterrows():
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
        for idx, row in df_merged.iterrows():
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
    VALID_POSTAL_CODES = df_charging_stations_copy['PLZ'].astype(str).tolist()
    
    
    # Call the init file method (creates the file if it doesn't yet exist)
    initialize_file()
    
    # Load suggestions into memory
    if "suggestions" not in st.session_state:
        st.session_state["suggestions"] = load_suggestions()

    # Sidebar menu
    option = st.sidebar.radio("Choose an option:", ["Submit a Suggestion", "View Suggestions", "Clear Suggestions"])

    if option == "Submit a Suggestion":
        st.header("Submit Your Suggestion")
        
        # Text input for the suggestion
        postal_code = st.text_input("Enter PLZ:")
        suggestion = st.text_area("Write your suggestion here:")
        
        # Button to submit the suggestion
        if st.button("Submit Suggestion"):
            if suggestion.strip() and postal_code.strip():  # Check if the suggestion is not empty
                if postal_code.strip() in VALID_POSTAL_CODES:
                    st.session_state["suggestions"].append({
                        "Text": suggestion.strip(),
                        "PLZ": postal_code.strip()})
                    save_suggestions(st.session_state["suggestions"])  # Save to file
                    st.success("Thank you for your suggestion!")
                else:
                    st.error("Invalid PLZ.")
            else:
                st.warning("Suggestion and PLZ cannot be empty.")

    elif option == "View Suggestions":
        st.header("Suggestions List")
        
        if st.session_state["suggestions"]:
            # Input for filtering by postal code
            filter_postal_code = st.text_input("Filter by postal code")
 
            # Filter or sort suggestions based on postal code
            filtered_suggestions = (
                sorted(st.session_state["suggestions"], key = lambda x: x["PLZ"])
                if not filter_postal_code
                else [
                    s for s in st.session_state["suggestions"]
                    if s["PLZ"] == filter_postal_code.strip()
                ]
            )
            
            # Display each suggestion
            if filtered_suggestions:
                for i, suggestion in enumerate(filtered_suggestions, 1):
                    st.write(f"{i}. {suggestion["Text"]} - PLZ: {suggestion["PLZ"]}")
            else:
                st.info("No suggestions match the given postal code.")
        else:
            st.info("No suggestions have been submitted yet.")
    
    elif option == "Clear Suggestions":
        st.header("Input the Admin Password To Clear Suggestions")
        
        # Take user password
        password_input = st.text_input("Password:", type="password")
        
        # Clear suggestions & Update state
        clear_suggestions(password_input.strip())
        st.session_state["suggestions"] = load_suggestions()

