# Methods associated suggestions that deploy the streamlit app


import streamlit as st
from core.suggestions_methods.SuggestionsMethods import initialize_file, load_suggestions, save_suggestions, clear_suggestions_file


def submit_a_suggestion(VALID_POSTAL_CODES):
    '''
    Writes to the JSON file a suggestion that the user wants to submit
    Inputs: VALID_POSTAL_CODES - a list of the postal codes contained in our data
    Outputs: None
    Postcondition: The suggestion file is written and the streamlit app is deployed
    '''
    st.sidebar.header("Submit Your Suggestion")
    
    # Text input for the suggestion
    postal_code = st.sidebar.text_input("Enter PLZ:")
    suggestion = st.sidebar.text_area("Write your suggestion here:")
        
    # Button to submit the suggestion
    if st.sidebar.button("Submit Suggestion"):
        if suggestion.strip() and postal_code.strip():  # Check if the suggestion is not empty
            if postal_code.strip() in VALID_POSTAL_CODES:
                st.session_state["suggestions"].append({
                    "Text": suggestion.strip(),
                    "PLZ": postal_code.strip()})
                save_suggestions(st.session_state["suggestions"])  # Save to file
                st.sidebar.success("Thank you for your suggestion!")
            else:
                st.sidebar.error("Invalid PLZ.")
        else:
            st.sidebar.warning("Suggestion and PLZ cannot be empty.")


# -----------------------------------------------------------------------

def view_suggestions():
    '''
    Allows the user to view suggestions and filter by PLZ
    Inputs: None
    Outputs: None
    Postconditions: The session state suggestions is read and the suggestions are displayed
        with the option to filter by PLZ
    '''
    st.sidebar.header("Suggestions List")
    
    if st.session_state["suggestions"]:
        # Input for filtering by postal code
        filter_postal_code = st.sidebar.text_input("Filter by postal code")
 
        # Filter or sort suggestions based on postal code
        filtered_suggestions = (
            sorted(st.session_state["suggestions"], key = lambda x: x["PLZ"])
            if not filter_postal_code
            else [
                s for s in st.session_state["suggestions"]
                if s["PLZ"] == filter_postal_code.strip()
            ]
        )
            
        # Display each suggestion
        if filtered_suggestions:
            for i, suggestion in enumerate(filtered_suggestions, 1):
                st.sidebar.write(f"{i}. {suggestion['Text']} - PLZ: {suggestion['PLZ']}")
        else:
            st.sidebar.info("No suggestions match the given postal code.")
    else:
        st.sidebar.info("No suggestions have been submitted yet.")

# -----------------------------------------------------------------------

def clear_suggestions():
    '''
    Takes a user password, and when correct, wipes the JSON file storing suggestions
    Inputs: None
    Outputs: None
    Postconditions: The JSON file storing suggestions is cleared and the session state is updated if the password is correct
    '''
    st.sidebar.header("Input the Admin Password To Clear Suggestions")
        
    # Take user password
    password_input = str(st.sidebar.text_input("Password:", type="password").strip())
        
    # Clear suggestions & Update state
    clear_suggestions_file(password_input)
    st.sidebar.empty()
    st.session_state["suggestions"] = load_suggestions()
