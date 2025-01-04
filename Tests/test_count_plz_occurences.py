import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from core.methods import  count_plz_occurrences


class TestCountPlzOccurrences(unittest.TestCase):

    def test_basic_case(self):
        # Test with a basic DataFrame containing unique PLZs
        data = {
            'PLZ': [10010, 10010, 10020, 10020, 10020, 10030],
            'geometry': ['geom1', 'geom1', 'geom2', 'geom2', 'geom2', 'geom3']
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

    def test_empty_dataframe(self):
        # Test that it doesnt crash with empty df

        df = pd.DataFrame(columns=['PLZ', 'geometry'])
        expected_df = pd.DataFrame(columns=['PLZ', 'Number', 'geometry'])
        expected_df = expected_df.astype({'Number': 'int64'})

        result_df = count_plz_occurrences(df)
        assert_frame_equal(result_df, expected_df)