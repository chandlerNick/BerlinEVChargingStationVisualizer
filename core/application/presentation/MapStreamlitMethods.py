# Methods associated the map that help deploy the streamlit app


import streamlit as st
import folium
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import geopandas as gpd
from core.domain.demand_methods.DemandMethods import DemandMethod


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
    df_merged['Demand'] = demander.robert_demands(df_merged['Einwohner'], df_merged['Number'])
        
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


