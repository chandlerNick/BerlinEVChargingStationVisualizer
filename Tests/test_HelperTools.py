from unittest import TestCase
from unittest.mock import patch, call
import pickle
import time
from core.infrastructure.HelperTools import pickle_in, pickle_out, binom, \
    intersect, remNanFromListFloat, remNullItemsFromList, remNanFromDict, \
    remNullItemsFromDict, timer

FILENAME = "datasets/pickler.pkl"
TO_SAVE = "This is a string object we will pickle up"

def sample_function_for_timing(x, y):
    time.sleep(0.1)



class TestHelperTools(TestCase):

    def test_pickling(self):

        # HelperTools result
        pickle_out(TO_SAVE, FILENAME)
        helper_tools_result = pickle_in(FILENAME)
        
        # Ground truth result (actual)
        with open(FILENAME, "wb") as file:
            pickle.dump(TO_SAVE, file)

        with open(FILENAME, 'rb') as file:
            ground_truth_result = pickle.load(file)

        self.assertEqual(helper_tools_result, ground_truth_result)
    
    
    def test_binom(self):
        helper_tools_result = binom(6, 3)
        
        self.assertEqual(helper_tools_result, 20)
        
    def test_intersect(self):
        helper_tools_result = intersect({1, 2, 3}, {3, 4, 5})
        
        self.assertEqual(helper_tools_result, [3])
        
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





