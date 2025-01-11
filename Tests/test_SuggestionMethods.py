import unittest
import os
import json
from pathlib import Path
from core.domain.suggestions_methods.SuggestionsMethods import initialize_suggestions_file, load_suggestions, save_suggestions, clear_suggestions_file, overwrite_file


SUGGESTIONS_FILE = "Tests/datasets/suggestions.json"


class TestSuggestionMethods(unittest.TestCase):

    def setUp(self, suggestions_file = SUGGESTIONS_FILE):

        # Ensure the test file doesn't exist before running the test
        if Path(suggestions_file).exists():
            os.remove(suggestions_file)

    def tearDown(self,suggestions_file = SUGGESTIONS_FILE):

        # Remove the file after testing
        if Path(suggestions_file).exists():
            os.remove(suggestions_file)

    def test_load_empty_suggestions(self, suggestions_file = SUGGESTIONS_FILE):
        '''Test loading suggestions when the file is empty '''

        initialize_suggestions_file(suggestions_file)  # Create an empty file
        suggestions = load_suggestions(suggestions_file)
        self.assertEqual(suggestions, [])

    def test_load_existing_suggestions(self, suggestions_file = SUGGESTIONS_FILE):
        '''Test if existing suggestions can be accessed correctly '''

        # Test loading suggestions when the file has data
        data = ["Suggestion 1", "Suggestion 2"]
        with open(suggestions_file, "w") as file:
            json.dump(data, file)

        suggestions = load_suggestions(suggestions_file)
        self.assertEqual(suggestions, data)


    def test_initialize_suggestions_file(self):

        '''Test if the suggestions file gets initialized correclty'''

        # Ensure the file doesn't exist before the test
        if Path(SUGGESTIONS_FILE).exists():
            os.remove(SUGGESTIONS_FILE)

        initialize_suggestions_file(SUGGESTIONS_FILE)

        # Check that the file was created
        self.assertTrue(Path(SUGGESTIONS_FILE).exists())

        # Check that the file contains an empty list
        with open(SUGGESTIONS_FILE, "r") as file:
            data = json.load(file)
            self.assertEqual(data, [])

        # Clean up after the test
        os.remove(SUGGESTIONS_FILE)


    def test_save_suggestions_creates_file(self):
        """Test if save_suggestions creates a new file with correct content."""
        suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        save_suggestions(suggestions, SUGGESTIONS_FILE)

        self.assertTrue(
            Path(SUGGESTIONS_FILE).exists())  # Check if file was created

        # Load the saved suggestions and verify content
        loaded_suggestions = load_suggestions(SUGGESTIONS_FILE)
        self.assertEqual(loaded_suggestions, suggestions)

    def test_save_suggestions_overwrites_file(self):
        """Test if save_suggestions correctly overwrites an existing file."""
        initial_suggestions = ["Old Suggestion"]
        save_suggestions(initial_suggestions, SUGGESTIONS_FILE)

        # Verify initial content
        loaded_suggestions = load_suggestions(SUGGESTIONS_FILE)
        self.assertEqual(loaded_suggestions, initial_suggestions)

        # Overwrite with new suggestions
        new_suggestions = ["New Suggestion 1", "New Suggestion 2"]
        save_suggestions(new_suggestions, SUGGESTIONS_FILE)

        # Verify new content
        loaded_suggestions = load_suggestions(SUGGESTIONS_FILE)
        self.assertEqual(loaded_suggestions, new_suggestions)


    def test_clear_suggestions_file_correct_password(self):
        """Test if clear_suggestions_file clears the file when correct password is given."""
        suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        save_suggestions(suggestions, SUGGESTIONS_FILE) # Save mock suggestions

        clear_suggestions_file(password="1234", suggestions_file=SUGGESTIONS_FILE)
        loaded_suggestions = load_suggestions(SUGGESTIONS_FILE)
        self.assertEqual(loaded_suggestions, [])  # Check if file is cleared

    def test_clear_suggestions_file_incorrect_password(self):
        """Test if clear_suggestions_file does not clear the file when incorrect password is given."""
        suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        save_suggestions(suggestions, SUGGESTIONS_FILE) # Save mock suggestions
        initial_suggestion_file = load_suggestions(SUGGESTIONS_FILE)

        clear_suggestions_file(password="wrong_password", suggestions_file=SUGGESTIONS_FILE)
        loaded_suggestions = load_suggestions(SUGGESTIONS_FILE)
        self.assertEqual(loaded_suggestions, initial_suggestion_file)  # Check if file is unchanged


    def test_overwrite_file(self):
        """Test if overwrite_file correctly writes an empty list to the file."""
        overwrite_file(SUGGESTIONS_FILE)

        # Load the content of the file to verify it is empty
        with open(SUGGESTIONS_FILE, "r") as file:
            content = json.load(file)

        self.assertEqual(content, [])  # The file should contain an empty list


if __name__ == '__main__':
    unittest.main()
