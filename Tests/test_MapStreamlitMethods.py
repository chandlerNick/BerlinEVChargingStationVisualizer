import unittest
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from branca.colormap import LinearColormap
from core.presentation.MapStreamlitMethods import create_residents_layer, create_demand_layer, \
    create_charging_stations_layer


class TestMapStreamLitMethods(unittest.TestCase):
    """Test if the map is generated correctly and color ranges are correct"""

    def setUp(self):
        # Sample geodataframe with minimal data for testing
        self.df_population = gpd.GeoDataFrame({
                'PLZ': ['10115', '10117'],
                'Einwohner': [1000, 2000],
                'geometry': [Polygon([(13.0, 52.5), (13.1, 52.5), (13.1, 52.6),
                                      (13.0, 52.6)]),
                             Polygon([(13.2, 52.5), (13.3, 52.5), (13.3, 52.6),
                                      (13.2, 52.6)])]
        })

        self.df_merged = gpd.GeoDataFrame({
                'PLZ': ['10115', '10117'],
                'Einwohner': [1000, 2000],
                'Number': [10, 20],
                'geometry': [Polygon([(13.0, 52.5), (13.1, 52.5), (13.1, 52.6),
                                      (13.0, 52.6)]),
                             Polygon([(13.2, 52.5), (13.3, 52.5), (13.3, 52.6),
                                      (13.2, 52.6)])]
        })

        # Create an empty folium map for testing
        self.folium_map = folium.Map(location = [52.5, 13.3], zoom_start = 10)

    def test_create_residents_layer(self):
        # Call the function
        color_map, result_map = create_residents_layer(self.df_population,
                                                       self.folium_map)

        # Assert that the result is a folium Map object
        self.assertIsInstance(result_map, folium.Map)

        # Assert that the color_map is a LinearColormap
        self.assertIsInstance(color_map, LinearColormap)

        # Check that the color map range is correct
        self.assertEqual(color_map.vmin, self.df_population['Einwohner'].min())
        self.assertEqual(color_map.vmax, self.df_population['Einwohner'].max())


    def test_create_charging_stations_layer(self):
        # Call the function
        color_map, result_map = create_charging_stations_layer(self.df_merged,
                                                               self.folium_map)

        # Assert that the result is a folium Map object
        self.assertIsInstance(result_map, folium.Map)

        # Assert that the color_map is a LinearColormap
        self.assertIsInstance(color_map, LinearColormap)

        # Check that the color map range is correct
        self.assertEqual(color_map.vmin, self.df_merged['Number'].min())
        self.assertEqual(color_map.vmax, self.df_merged['Number'].max())

