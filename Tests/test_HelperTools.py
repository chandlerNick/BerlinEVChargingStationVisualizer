from unittest import TestCase
from unittest.mock import patch, call
import pickle
import time
from core.HelperTools import pickle_in, pickle_out, binom, intersect, remNanFromListFloat, remNullItemsFromList, remNanFromDict, remNullItemsFromDict, timer

FILENAME = "datasets/pickler.pkl"
TO_SAVE = "This is a string object we will pickle up"

def sample_function_for_timing(x, y):
    time.sleep(0.1)



class TestHelperTools(TestCase):

    def test_pickling(self):
        # Initialization
        ground_truth_result = None
        helper_tools_result = None
        
        # HelperTools result
        pickle_out(TO_SAVE, FILENAME)
        helper_tools_result = pickle_in(FILENAME)
        
        # Ground truth result (actual)
        with open(FILENAME, "rwb") as file:
            pickle.dump(TO_SAVE, file)
            ground_truth_result = pickle.load(file)

        self.assertEqual(helper_tools_result, ground_truth_result)
    
    
    def test_binom(self):
        helper_tools_result = binom(6, 3)
        
        self.assertEqual(helper_tools_result, 20)
        
    def test_intersect(self):
        helper_tools_result = intersect({1, 2, 3}, {3, 4, 5})
        
        self.assertEqual(helper_tools_result, {3})
        
    def test_remove_from_lists(self):
        helper_test_result_1 = remNanFromListFloat([float("nan"), 0.3, 1.2, 3.3])
        helper_test_result_2 = remNullItemsFromList([None, 1, 2, 3])
        
        self.assertEqual(helper_test_result_1, [0.3, 1.2, 3.3])
        self.assertEqual(helper_test_result_2, [1, 2, 3])

    def test_remove_from_dicts(self):
        helper_test_result_1 = remNanFromDict({'key1': float("nan"), 'key2': 0.3, 'key3': 1.4})
        helper_test_result_2 = remNullItemsFromDict({'key1': None, 'key2': 0.3, 'key3': 1.4})
        
        self.assertEqual(helper_test_result_1, {'key2': 0.3, 'key3': 1.4})
        self.assertEqual(helper_test_result_2, {'key2': 0.3, 'key3': 1.4})


    @patch("builtins.print")
    def test_timer_wrapper(self, mock_print):
        # Test correctness of original function
        result = sample_function_for_timing(3, 4)
        self.assertEqual(result, 7, "The wrapper shouldn't alter functionality")
        
        # Test printing
        mock_print.assert_called_once()
        self.assertRegex(
            mock_print.call_args[0][0],
            r" ====> Duration \d+\.\d{2} secs: .*",
            "The wrapper prints the timing information"
        )
        
        # Test Metadata -- metadata is unchanged by wrapper
        self.assertEqual(sample_function_for_timing.__name__, "sample_function_for_timing")

        
