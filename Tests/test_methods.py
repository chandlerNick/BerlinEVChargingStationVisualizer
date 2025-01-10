# Tests for the methods.py file
# 06.01.2024

from unittest import TestCase
from core.methods import preprop_lstat, sort_by_plz_add_geometry
import pandas as pd
import os
from pandas.testing import assert_frame_equal
from config import pdict
from geopandas.testing import assert_geodataframe_equal
from core.methods import  count_plz_occurrences



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


    def test_count_plz_occurences_basic_case(self):
        # Test with a basic DataFrame containing unique PLZs
        data = {
                'PLZ': [10010, 10010, 10020, 10020, 10020, 10030],
                'geometry': ['geom1', 'geom1', 'geom2', 'geom2', 'geom2',
                             'geom3']
        }
        df = pd.DataFrame(data)
        expected_data = {
                'PLZ': [10010, 10020, 10030],
                'Number': [2, 3, 1],
                'geometry': ['geom1', 'geom2', 'geom3']
        }
        expected_df = pd.DataFrame(expected_data)

        result_df = count_plz_occurrences(df)
        assert_frame_equal(result_df, expected_df)

    def test_count_plz_occurences_empty_dataframe(self):
        # Test that it doesnt crash with empty df

        df = pd.DataFrame(columns = ['PLZ', 'geometry'])
        expected_df = pd.DataFrame(columns = ['PLZ', 'Number', 'geometry'])
        expected_df = expected_df.astype({'Number': 'int64'})

        result_df = count_plz_occurrences(df)
        assert_frame_equal(result_df, expected_df)