# Methods associated with the suggestions input
# 06.01.2025



import json
from pathlib import Path


# Define the path to the suggestions file
SUGGESTIONS_FILE = "/mount/src/berlinevchargingstationvisualizer/datasets/suggestions.json"

# -----------------------------------------------------------------------

# Function to initialize the JSON file
def initialize_file():
    '''
    Initializes the JSON file if it isn't already
    Input: None
    Output: None
    Postcondition: The appropriate file for storing suggestions is created
    '''
    if not Path(SUGGESTIONS_FILE).exists():  # Check if the file exists
        with open(SUGGESTIONS_FILE, "w") as file:
            json.dump([], file)  # Create an empty list in the file


# -----------------------------------------------------------------------

# Function to load suggestions from the file
def load_suggestions():
    '''
    Loads the suggestions from the json file at the specified path
    Input:
    Output:
    '''
    initialize_file()
    if Path(SUGGESTIONS_FILE).exists():
        with open(SUGGESTIONS_FILE, "r") as file:
            return json.load(file)
    return []


# -----------------------------------------------------------------------
# Function to save suggestions to the file


def save_suggestions(suggestions):
    '''
    Save suggestions to the json file at the specified path
    Input: suggestions
    Output: None
    Postconditions: The file at SUGGESTIONS_FILE is updated via a JSON dump
    '''
    with open(SUGGESTIONS_FILE, "w+") as file:
        json.dump(suggestions, file)
