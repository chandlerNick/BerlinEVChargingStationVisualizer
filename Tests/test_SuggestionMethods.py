import unittest
import os
import json
from pathlib import Path
from core.suggestions_methods.SuggestionsMethods import initialize_suggestions_file, load_suggestions


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
        # Test loading suggestions when the file is empty
        initialize_suggestions_file(suggestions_file)  # Create an empty file
        suggestions = load_suggestions(suggestions_file)
        self.assertEqual(suggestions, [])

    def test_load_existing_suggestions(self, suggestions_file = SUGGESTIONS_FILE):

        # Test loading suggestions when the file has data
        data = ["Suggestion 1", "Suggestion 2"]
        with open(suggestions_file, "w") as file:
            json.dump(data, file)

        suggestions = load_suggestions(suggestions_file)
        self.assertEqual(suggestions, data)


    def test_initialize_suggestions_file(self):

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


if __name__ == '__main__':
    unittest.main()
