
#currentWorkingDirectory = "C:\\(...)\\project1"
currentWorkingDirectory = "/mnt/c/Users/njcha/OneDrive/BHT/Semester1/AdvancedSoftwareEngineering/BerlinEVChargingStationVisualizer/"

# -----------------------------------------------------------------------------
import os
os.chdir(currentWorkingDirectory)
print("Current working directory\n" + os.getcwd())

import pandas                        as pd
import geopandas as gpd
from core import methods             as m1
from core import HelperTools         as ht

from config                          import pdict

# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""


    # Load in the respective datasets
    df_geodat_plz   = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'geodata_berlin_plz.csv'), delimiter=';')  #
    
    df_lstat        = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'Ladesaeulenregister.csv'), delimiter=';')
    df_lstat2       = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3      = m1.count_plz_occurrences(df_lstat2)
    
    df_residents    = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'plz_einwohner.csv'), delimiter=',')  #

    gdf_residents2  = m1.preprop_resid(df_residents, df_geodat_plz, pdict)
    
    
    
    # Run the app creator
    m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)
    
# -----------------------------------------------------------------------------------------------------------------------

    #


if __name__ == "__main__": 
    main()

