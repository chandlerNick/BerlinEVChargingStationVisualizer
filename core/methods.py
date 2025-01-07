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
from core.demand_methods.DemandMethods import DemandMethod
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


def create_residents_layer(df_population, folium_map):
    '''
    Creates the residents layer
    Inputs:
        - df_population: A geodataframe with location and population information
        - folium_map: The folium map on which to draw the desired population map
    Outputs:
        - color_map: a color_map to be added
        - folium_map: the folium_map to be drawn
    Postconditions: The Residents layer of the folium_map is created
    '''    
    # Create a color map for Residents using LinearColormap from branca
    color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=df_population['Einwohner'].min(), vmax=df_population['Einwohner'].max())

    # Add polygons to the map for Residents
    for idx, row in df_population.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color_map(row['Einwohner']): {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
        ).add_to(folium_map)

    return color_map, folium_map


# ------------------------------------------------------------------------

def write_demand_formula_to_screen(formula, variables):
    '''
    Writes the two latex statments to the screen
    Inputs:
        - Formula denoting how the demand function is constructed
        - Variables specifying the parts of the demand function
    Outputs: None
    Postconditions: Demand formula is written to the screen
    '''
    st.text("Demand Formula")
    st.latex(formula)
    st.text("Constituent Variables")
    st.latex(variables)


# ------------------------------------------------------------------------


def create_demand_layer(df_merged, folium_map):
    '''
    Creates the demand layer
    Inputs:
        - df_merged: a dataframe containing information about the number of residents and the number of charging stations
            In addition to the geographic data of Berlin
        - folium_map: the empty folium_map to be populated
    Outputs:
        - color_map: a color_map to be added
        - folium_map: the folium_map to be drawn
    Postconditions: The Demand layer of the folium_map is created
    '''
    # Create DemandMethod Object
    demander = DemandMethod()
    
    # Implement Demand
    df_merged['Demand'] = demander.robert_demands(df_merged['Number'], df_merged['Einwohner'])
        
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
        ).add_to(folium_map)
            
    # Write DemandMethod formula to screen
    write_demand_formula_to_screen(demander.latex_formula, demander.latex_variables)

    return color_map, folium_map

# -----------------------------------------------------------------------


def create_charging_stations_layer(df_merged, folium_map):
    '''
    Creates the charging stations layer of the map
    Inputs: 
        - df_merged: a dataframe containing information about the number of residents and the number of charging stations
            in addition to the geographic data of Berlin
        - folium_map: the empty folium_map to be populated
    Outputs:
        - color_map: a color_map to be added
        - folium_map: the folium_map to be drawn
    Postconditions: The Charging Stations layer of the folium_map is created
    '''
    # Create a color map for Numbers
    color_map = LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red', 'magenta'], vmin=df_merged['Number'].min(), vmax=df_merged['Number'].max())

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
        ).add_to(folium_map)

    return color_map, folium_map

# ------------------------------------------------------------------------

def submit_a_suggestion(VALID_POSTAL_CODES):
    '''
    Writes to the JSON file a suggestion that the user wants to submit
    Inputs: VALID_POSTAL_CODES - a list of the postal codes contained in our data
    Outputs: None
    Postcondition: The suggestion file is written and the streamlit app is deployed
    '''
    st.sidebar.header("Submit Your Suggestion")
    
    # Text input for the suggestion
    postal_code = st.sidebar.text_input("Enter PLZ:")
    suggestion = st.sidebar.text_area("Write your suggestion here:")
        
    # Button to submit the suggestion
    if st.sidebar.button("Submit Suggestion"):
        if suggestion.strip() and postal_code.strip():  # Check if the suggestion is not empty
            if postal_code.strip() in VALID_POSTAL_CODES:
                st.session_state["suggestions"].append({
                    "Text": suggestion.strip(),
                    "PLZ": postal_code.strip()})
                save_suggestions(st.sidebar.session_state["suggestions"])  # Save to file
                st.sidebar.success("Thank you for your suggestion!")
            else:
                st.sidebar.error("Invalid PLZ.")
        else:
            st.sidebar.warning("Suggestion and PLZ cannot be empty.")


# -----------------------------------------------------------------------

def view_suggestions():
    '''
    Allows the user to view suggestions and filter by PLZ
    Inputs: None
    Outputs: None
    Postconditions: The session state suggestions is read and the suggestions are displayed
        with the option to filter by PLZ
    '''
    st.sidebar.header("Suggestions List")
    
    #st.session_state["suggestions"] = load_suggestions()
    
    if st.session_state["suggestions"]:
        # Input for filtering by postal code
        filter_postal_code = st.sidebar.text_input("Filter by postal code")
 
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
                st.sidebar.write(f"{i}. {suggestion["Text"]} - PLZ: {suggestion["PLZ"]}")
        else:
            st.sidebar.info("No suggestions match the given postal code.")
    else:
        st.sidebar.info("No suggestions have been submitted yet.")

# -----------------------------------------------------------------------

def clear_suggestions():
    '''
    Takes a user password, and when correct, wipes the JSON file storing suggestions
    Inputs: None
    Outputs: None
    Postconditions: The JSON file storing suggestions is cleared and the session state is updated if the password is correct
    '''
    st.sidebar.header("Input the Admin Password To Clear Suggestions")
        
    # Take user password
    password_input = st.sidebar.text_input("Password:", type="password")
        
    # Clear suggestions & Update state
    clear_suggestions(password_input.strip())
    st.session_state["suggestions"] = load_suggestions()
    st.sidebar.empty()
    if password_input.strip() == "1234":
        st.sidebar.write("Password Accepted")
    st.sidebar.info("Suggestions cleared")

# -----------------------------------------------------------------------

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
        
        submit_a_suggestion(VALID_POSTAL_CODES)

    elif option == "View Suggestions":
        
        view_suggestions()
    
    elif option == "Clear Suggestions":

        clear_suggestions()
        st.sidebar.empty()
        
