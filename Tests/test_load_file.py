import unittest
import os
import json
from pathlib import Path
from unittest.mock import patch
from core.methods import initialize_file, load_suggestions


SUGGESTIONS_FILE = "datasets/suggestions.json"


class TestLoadSuggestions(unittest.TestCase):

    def setUp(self):

        # Ensure the test file doesn't exist before running the test
        if Path(SUGGESTIONS_FILE).exists():
            os.remove(SUGGESTIONS_FILE)

    def tearDown(self):

        # Remove the file after testing
        if Path(SUGGESTIONS_FILE).exists():
            os.remove(SUGGESTIONS_FILE)

    def test_load_empty_suggestions(self):

        # Test loading suggestions when the file is empty
        initialize_file()  # Create an empty file
        suggestions = load_suggestions()
        self.assertEqual(suggestions, [])

    def test_load_existing_suggestions(self):

        # Test loading suggestions when the file has data
        data = ["Suggestion 1", "Suggestion 2"]
        with open(SUGGESTIONS_FILE, "w") as file:
            json.dump(data, file)

        suggestions = load_suggestions()
        self.assertEqual(suggestions, data)


if __name__ == '__main__':
    unittest.main()
