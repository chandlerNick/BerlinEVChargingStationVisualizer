import unittest
# from demand_file import calculate_demand
import pandas as pd
from core.domain.demand_methods.DemandMethods import DemandMethod

dm = DemandMethod()

class TestDemandFunction(unittest.TestCase):


    def test_demand_calculation(self):
        # If the inputs are as expected
        # calculate the demand for several PLZ by hand and assert that it's the same

        # PLZ 14109 with 10049 inhabitants and 23 charging stations
        demand = dm.robert_demands(pd.DataFrame([[10049]]), pd.DataFrame([[23]]) ).iloc[0,0]
        actual_demand = -13

        self.assertEqual(demand, actual_demand)


        # PLZ 13125 with 31379 inhabitants and 16 charging stations
        demand = dm.robert_demands(pd.DataFrame([[31379]]),pd.DataFrame([[16]])).iloc[0, 0]
        actual_demand = 15

        self.assertEqual(demand, actual_demand)


    def test_demand_with_0_stations(self):

        # Test with 0 charrging stations and 31379 residents - make sure this does compute correctly and does not throw an error

        demand = dm.robert_demands(pd.DataFrame([[31379]]), pd.DataFrame([[0]])).iloc[0, 0]
        actual_demand = 31
        self.assertEqual(demand, actual_demand)


    def test_demand_with_0_residents(self):

        # Test with 10 charging stations and 0 residents - make sure this does compute correctly and does not throw an error

        demand = dm.robert_demands(pd.DataFrame([[0]]), pd.DataFrame([[10]])).iloc[0, 0]
        actual_demand = -10
        self.assertEqual(demand, actual_demand)


    def test_demand_wrong_input(self):

        # Make sure an incorrect input leads to an exception

        self.assertRaises(Exception, dm.robert_demands, pd.DataFrame([["10"]]), pd.DataFrame([[0]]))


    def test_demand_residents_negative_input(self):

        # Make sure a negative input value for residents leads to an exception

        self.assertRaises(ValueError, dm.robert_demands, pd.DataFrame([[-10]]), pd.DataFrame([[10]]))


    def test_demand_cs_negative_input(self):

        # Make sure a negative input value for number of stations leads to an exception

        self.assertRaises(ValueError, dm.robert_demands, pd.DataFrame([[10]]), pd.DataFrame([[-10]]))



if __name__ == '__main__':
    unittest.main()
