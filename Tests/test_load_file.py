import unittest
import os
import json
from pathlib import Path
from core.suggestions_methods.SuggestionsMethods import initialize_suggestions_file, load_suggestions


SUGGESTIONS_FILE = "datasets/suggestions.json"


class TestLoadSuggestions(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
