# Functions associated with the demand geovisualizer
# 06.01.2025


# Robert's demand function
def robert_demands(gdf_residents_preprocessed, gdf_charging_station_counts):
    """
    Calculates Charging Station Demand per Postal Code
    Inputs: gdf_residents_preprocessed - residents vector; gdf_charging_station_counts - charging station counts vector
    Outputs: Vector of charging station demand as integers
    Postconditions: Demand is calculated using the formula (0.01 * station counts / 10) - residents

    Formula: (EV * P / EVPCS) - CS
    with:
    EV = Electric Vehicles per resident (currently 0.01)
    P = Population per postal code
    EVPCS = Electric Vehicles per Charging Station (recommended are 10)
    CS = Charging Stations that already exist in the postal code area

    """

    return (0.01 * gdf_residents_preprocessed / 10).sub(gdf_charging_station_counts).astype(int)


