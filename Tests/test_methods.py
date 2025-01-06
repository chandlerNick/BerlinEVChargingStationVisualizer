# Tests for the methods.py file
# 06.01.2024

from unittest import TestCase
from unittest.mock import patch, MagicMock
import streamlit as st
from core.methods import make_streamlit_electric_Charging_resid, preprop_lstat, sort_by_plz_add_geometry
import pandas as pd
import os
from config import pdict
import geopandas as gpd
from geopandas.testing import assert_geodataframe_equal



class TestMethods(TestCase):
    
    def test_preprop_lstat(self):
        # Read in datasets
        df_lstat        = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'Ladesaeulenregister.csv'), delimiter=';')
        df_geodat_plz   = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'geodata_berlin_plz.csv'), delimiter=';')

        # Obtain method preprocessing result
        method_result = preprop_lstat(df_lstat, df_geodat_plz, pdict)
        
        # Preprocess here
        dframe2 = df_lstat.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
        dframe2.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

        dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str)
        dframe2['Längengrad'] = dframe2['Längengrad'].astype(str)
        
        dframe2['Breitengrad'] = dframe2['Breitengrad'].str.replace(',', '.')
        dframe2['Längengrad'] = dframe2['Längengrad'].str.replace(',', '.')

        dframe3 = dframe2[(dframe2["Bundesland"] == 'Berlin') & 
                      (dframe2["PLZ"] > 10115) &  
                      (dframe2["PLZ"] < 14200)]

        manual_result = sort_by_plz_add_geometry(dframe3, df_geodat_plz, pdict)

        # Assertion - uses geopandas testing to verify
        try:
            assert_geodataframe_equal(manual_result, method_result)
        except AssertionError as e:
            self.fail(f"GeoDataFrames are not equal: {e}")

