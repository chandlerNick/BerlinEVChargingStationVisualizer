import pandas as pd
import geopandas as gpd
import core.infrastructure.HelperTools as ht
import folium
import streamlit as st
from streamlit_folium import folium_static
from core.domain.suggestions_methods.SuggestionsMethods import \
    initialize_suggestions_file, load_suggestions, SUGGESTIONS_FILE
from core.application.presentation.SuggestionsStreamlitMethods import submit_a_suggestion, view_suggestions, clear_suggestions
from core.application.presentation.MapStreamlitMethods import create_residents_layer, create_demand_layer, create_charging_stations_layer

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

def merge_geo_dataframes(df_charging_stations, df_population):
    '''
    Merges the charging stations and population dataframes and fills NA's with 0
    Inputs:
        - df_charging_stations: A geodataframe sorted by PLZ and containing information about the charging stations
        - df_population: A geodataframe sorted by PLZ and containing information about the population
    Outputs: A merged geodataframe
    '''

    # Merge resident and charging station data
    df_charging_stations['PLZ'] = df_charging_stations['PLZ'].astype(int)
    df_charging_stations = df_charging_stations.iloc[:, 0:2]
    df_merged = df_population.merge(df_charging_stations, on='PLZ', how='left')

    # Fill NaN values with 0
    df_merged['Number'] = df_merged['Number'].fillna(0)
    
    return df_merged

# -------------------------------------------------------------------------

@ht.timer
def make_streamlit_electric_Charging_resid(df_charging_stations, df_population, suggestions_file = SUGGESTIONS_FILE):
    """
    Makes Streamlit App with Heatmap of Electric Charging Stations and Residents
    Inputs: 
        - df_charging_stations: A geodataframe sorted by PLZ and containing information about the charging stations
        - df_population: A geodataframe sorted by PLZ and containing information about the population
    Outputs: None
    Postconditions: Streamlit app is built and deployed
    """
    
    # Process data
    df_charging_stations_copy = df_charging_stations.copy()
    df_population_copy = df_population.copy()
    df_merged = merge_geo_dataframes(df_charging_stations_copy, df_population_copy)

    # Streamlit app
    st.title('Heatmaps: Electric Charging Stations and Residents')
    
    # --------------------------------------------------------------------
    # Map Section
    # --------------------------------------------------------------------


    # Create a radio button for layer selection
    layer_selection = st.radio("Select Layer", ("Residents", "Charging Stations", "Demand"))
    # Create a Folium map
    folium_map = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        
        color_map, folium_map = create_residents_layer(df_population_copy, folium_map)

    elif layer_selection == "Demand":

        color_map, folium_map = create_demand_layer(df_merged, folium_map)
    
    else:  # Must be Charging Stations
        
        color_map, folium_map = create_charging_stations_layer(df_merged, folium_map)
        
    # Add color map to the map
    color_map.add_to(folium_map)
    folium_static(folium_map, width=800, height=600)
    

    
    # ---------------------------------------------------------------------------------------------------------------------
    # Suggestions section - Continue debugging after interim submission feedback
    # ---------------------------------------------------------------------------------------------------------------------

    VALID_POSTAL_CODES = df_charging_stations_copy['PLZ'].astype(str).tolist()
    
    
    # Call the init file method (creates the file if it doesn't yet exist)
    initialize_suggestions_file(suggestions_file)
    
    # Load suggestions into memory
    if "suggestions" not in st.session_state:
        st.session_state["suggestions"] = load_suggestions(suggestions_file)

    # Sidebar menu
    option = st.sidebar.radio("Choose an option:", ["Submit a Suggestion", "View Suggestions", "Clear Suggestions"])

    if option == "Submit a Suggestion":
        
        submit_a_suggestion(VALID_POSTAL_CODES)

    elif option == "View Suggestions":
        
        view_suggestions()
    
    elif option == "Clear Suggestions":

        clear_suggestions()
        st.sidebar.empty()
        
