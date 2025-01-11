# Tests for the methods.py file
# 06.01.2024
from unittest import TestCase
from core.infrastructure.methods import preprop_lstat, sort_by_plz_add_geometry, \
    count_plz_occurrences, preprop_resid, \
    merge_geo_dataframes
import pandas as pd
import os
from pandas.testing import assert_frame_equal
from config import pdict
from geopandas.testing import assert_geodataframe_equal
import geopandas as gpd



SUGGESTIONS_FILE = 'datasets/suggestions.json'


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
        """ Test with a basic DataFrame containing unique PLZs """
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
        """Test that no error is thrown with an empty df"""

        df = pd.DataFrame(columns = ['PLZ', 'geometry'])
        expected_df = pd.DataFrame(columns = ['PLZ', 'Number', 'geometry'])
        expected_df = expected_df.astype({'Number': 'int64'})

        result_df = count_plz_occurrences(df)
        assert_frame_equal(result_df, expected_df)

    def setUp(self):
        """Set up test data for residents and geographic information."""

        # Setup for residents
        self.dfr = pd.DataFrame({
            "plz": [10115, 10178, 10435, 9999],
            "einwohner": [5000, 12000, 8000, 300],
            "lat": [52.5321, 52.5234, 52.5389, 52.0000],
            "lon": [13.3849, 13.4105, 13.4287, 13.0000]
        })

        self.dfg = pd.DataFrame({
            "PLZ": [10115, 10178, 10435],
            "geometry": ["POINT(13.3849 52.5321)", "POINT(13.4105 52.5234)", "POINT(13.4287 52.5389)"]
        })

        self.paramdict = {"geocode": "PLZ"}

        # SetUp for geodata
        # Sample data for df_population
        self.df_population = gpd.GeoDataFrame({
                'PLZ': [10115, 10117, 10119],
                'Population': [15000, 12000, 18000]
        })

        # Sample data for df_charging_stations
        self.df_charging_stations = pd.DataFrame({
                'PLZ': [10115, 10117],
                'Number': [10, 5]
        })

        # Expected output
        self.expected_output = pd.DataFrame({
                'PLZ': [10115, 10117, 10119],
                'Population': [15000, 12000, 18000],
                'Number': [10.0, 5.0, 0.0]
        })



    def test_preprop_resid(self):
        """Test preprocessing and merging of the DataFrame."""
        expected_df = gpd.GeoDataFrame({
            "PLZ": [10115, 10178, 10435],
            "Einwohner": [5000, 12000, 8000],
            "Breitengrad": ["52.5321", "52.5234", "52.5389"],
            "Längengrad": ["13.3849", "13.4105", "13.4287"],
            "geometry": gpd.GeoSeries.from_wkt([
                "POINT(13.3849 52.5321)",
                "POINT(13.4105 52.5234)",
                "POINT(13.4287 52.5389)"
            ])
        }, geometry='geometry')

        result = preprop_resid(self.dfr, self.dfg, self.paramdict)

        pd.testing.assert_frame_equal(result, expected_df)


    def test_merge_geo_dataframes(self):
        result = merge_geo_dataframes(self.df_charging_stations, self.df_population)
        assert_frame_equal(result, self.expected_output)

    def test_merge_with_empty_charging_stations(self):
        # Case where df_charging_stations is empty
        empty_charging_stations = pd.DataFrame(columns=['PLZ', 'Number'])
        expected_output = pd.DataFrame(self.df_population.copy())
        expected_output['Number'] = 0

        result = merge_geo_dataframes(empty_charging_stations, self.df_population)
        assert_frame_equal(result, expected_output)

    def test_merge_with_empty_population(self):
        # Case where df_population is empty
        empty_population = pd.DataFrame(columns=['PLZ', 'Population'])
        expected_output = pd.DataFrame(columns=['PLZ', 'Population', 'Number'])
        expected_output["Number"] = pd.to_numeric(expected_output["Number"])

        result = merge_geo_dataframes(self.df_charging_stations, empty_population)
        assert_frame_equal(result, expected_output)
