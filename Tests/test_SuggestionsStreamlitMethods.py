import unittest
from unittest.mock import patch
from core.application.presentation.SuggestionsStreamlitMethods import submit_a_suggestion

class TestSubmitSuggestion(unittest.TestCase):
    """Test behaviour for incorrectly submitted postal codes"""

    @patch("streamlit.sidebar")
    @patch("streamlit.session_state", new_callable = dict)
    def test_invalid_postal_code(self, mock_session_state, mock_sidebar):
        # Mocking inputs and session state
        mock_sidebar.text_input.side_effect = ["99999",
                                               "This is a test suggestion"]
        mock_sidebar.button.return_value = True
        mock_session_state["suggestions"] = []

        # List of valid postal codes
        VALID_POSTAL_CODES = ["10115", "10117", "10119"]

        # Call the function
        submit_a_suggestion(VALID_POSTAL_CODES)

        # Check that no suggestions were added
        self.assertEqual(len(mock_session_state["suggestions"]), 0)

        # Ensure an error message was displayed
        mock_sidebar.error.assert_called_once_with("Invalid PLZ.")

    @patch("streamlit.sidebar")
    @patch("streamlit.session_state", new_callable = dict)
    def test_empty_suggestion_or_postal_code(self, mock_session_state,
                                             mock_sidebar):
        # Mocking inputs and session state
        mock_sidebar.text_input.side_effect = ["", ""]
        mock_sidebar.button.return_value = True
        mock_session_state["suggestions"] = []

        # List of valid postal codes
        VALID_POSTAL_CODES = ["10115", "10117", "10119"]

        # Call the function
        submit_a_suggestion(VALID_POSTAL_CODES)

        # Check that no suggestions were added
        self.assertEqual(len(mock_session_state["suggestions"]), 0)

        # Ensure a warning message was displayed
        mock_sidebar.warning.assert_called_once_with(
            "Suggestion and PLZ cannot be empty.")

