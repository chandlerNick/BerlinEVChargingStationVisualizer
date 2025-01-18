# Methods associated with the suggestions input
# 06.01.2025
import json
from pathlib import Path
import os
import streamlit as st


# Define the path to the suggestions file
SUGGESTIONS_FILE = "/mount/src/berlinevchargingstationvisualizer/datasets/suggestions.json"


# ----------------------------------------------------------------------
def overwrite_file(suggestion_file = SUGGESTIONS_FILE):
    '''
    Writes an empty JSON file to SUGGESTIONS_FILE
    Inputs: None
    Outputs: None
    Postconditions: SUGGESTIONS_FILE is overwritten with an empty array
    '''
    with open(suggestion_file, "w") as file:
        json.dump([], file)  # Create an empty list in the file


# ----------------------------------------------------------------------

def clear_suggestions_file(password, suggestions_file = SUGGESTIONS_FILE):
    '''
    If the password matches, we can wipe the suggestions file
    Inputs: password, a string that is input on the streamlit UI
    Outputs: None
    Postconditions: The SUGGESTIONS_FILE is wiped if the correct password is given 
    '''
    if password == "12345":
        overwrite_file(suggestions_file)
        st.sidebar.info("Password Accepted")


# -----------------------------------------------------------------------

# Function to initialize the JSON file
def initialize_suggestions_file(suggestions_file = SUGGESTIONS_FILE):
    '''
    Initializes the JSON file if it isn't already
    Input: None
    Output: None
    Postcondition: An empty JSON file, SUGGESTIONS_FILE is created if it doesn't exist
    '''
    print(suggestions_file)
    if not Path(suggestions_file).exists():  # Check if the file exists
        overwrite_file(suggestions_file)


# -----------------------------------------------------------------------

# Function to load suggestions from the file
def load_suggestions(suggestions_file = SUGGESTIONS_FILE):
    '''
    Loads the suggestions from the json file at the specified path
    Input: None
    Output: 
        - Empty file if the SUGGESTIONS_FILE doesn't exist
        - Loaded JSON if the SUGGESTIONS_FILE does exist
    Postconditions: The SUGGESTIONS_FILE is loaded if it exists
    '''
    initialize_suggestions_file(suggestions_file)
    if Path(suggestions_file).exists():
        with open(suggestions_file, "r") as file:
            return json.load(file)
    return []


# -----------------------------------------------------------------------
# Function to save suggestions to the file


def save_suggestions(suggestions, suggestions_file = SUGGESTIONS_FILE):
    '''
    Save suggestions to the json file at the specified path
    Input: suggestions
    Output: None
    Postconditions: 
        - The file at SUGGESTIONS_FILE is updated via a JSON dump if it exists
        - A file SUGGESTIONS_FILE is created if it doesn't exist
    '''
    with open(suggestions_file, "w+") as file:
        json.dump(suggestions, file)
