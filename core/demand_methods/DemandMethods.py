# Functions associated with the demand geovisualizer
# 06.01.2025


# Robert's demand function
def robert_demands(dataframe_column_1, dataframe_column_2):
    '''
    Takes the charging station vector and the population vector and returns the demand based on the formula we devised
    Input: 
        - dataframe_column_1: 
        - dataframe_column_2: 
    Output: vector of charging station demand for each PLZ
    '''
    return (0.01 * dataframe_column_2 / 10).sub(dataframe_column_1).astype(int)