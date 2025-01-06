import os
import json
from pathlib import Path
from unittest import TestCase
from core.methods import initialize_file
from core.suggestions_methods.SuggestionsMethods import initialize_file, load_suggestions, save_suggestions, SUGGESTIONS_FILE

SUGGESTIONS_FILE = "datasets/suggestions.json"

class TestInitializeFile(TestCase):

    def test_initialize_file(self):

        # Ensure the file doesn't exist before the test
        if Path(SUGGESTIONS_FILE).exists():
            os.remove(SUGGESTIONS_FILE)

        initialize_file()

        # Check that the file was created
        self.assertTrue(Path(SUGGESTIONS_FILE).exists())

        # Check that the file contains an empty list
        with open(SUGGESTIONS_FILE, "r") as file:
            data = json.load(file)
            self.assertEqual(data, [])

        # Clean up after the test
        os.remove(SUGGESTIONS_FILE)
