import unittest
from unittest.mock import MagicMock, patch
import pathlib
import sys
import os

# Add the 'src' directory to the Python path to allow for absolute imports
project_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

from document_processing.pdf_processor import process_single_pdf
from models import Document

class TestPDFProcessor(unittest.TestCase):

    def setUp(self):
        """Set up a mock agent and a dummy PDF for testing."""
        # Create a mock agent that simulates the behavior of the real agent
        self.mock_agent = MagicMock()
        # When agent.run() is called, return a predefined dictionary
        self.mock_agent.run.return_value = {"title": "Mock Title", "authors": ["Author A", "Author B"]}

        # Create a dummy PDF file for testing purposes
        self.test_data_dir = project_root / 'tests' / 'test_data'
        self.test_data_dir.mkdir(exist_ok=True)
        self.dummy_pdf_path = self.test_data_dir / 'dummy.pdf'

        # For this test, we don't need a real PDF, just a path.
        # The image processing part that requires a real PDF will be patched.
        # However, let's create an empty file to make the path valid.
        with open(self.dummy_pdf_path, 'w') as f:
            f.write('')

    def tearDown(self):
        """Clean up any files created during the test."""
        if os.path.exists(self.dummy_pdf_path):
            os.remove(self.dummy_pdf_path)

    @patch('document_processing.pdf_processor.extract_full_text_from_pdf')
    @patch('document_processing.pdf_processor.extract_images_from_pdf')
    def test_process_single_pdf_with_mocks(self, mock_extract_images, mock_extract_text):
        """
        Test the process_single_pdf function with mocked text and image extraction.
        """
        # Configure the mock return values
        long_text = "This is a sufficiently long text chunk for testing purposes. " * 3
        mock_extract_text.return_value = long_text
        # Simulate finding no images
        mock_extract_images.return_value = []

        # Call the function with the dummy PDF path and the mock agent
        result_document = process_single_pdf(self.dummy_pdf_path, self.mock_agent)

        # --- Assertions ---
        # 1. Check if the result is a dictionary
        self.assertIsInstance(result_document, dict)

        # 2. Check if the mocked text was correctly assigned
        self.assertEqual(result_document["full_text"], long_text)

        # 3. Check if the agent's `run` method was called for metadata, tables and KG
        self.assertEqual(self.mock_agent.run.call_count, 3)

        # 4. Check that the agent's `analyze_image` method was not called, as no images were found
        # In the new structure, there is no analyze_image method on the agent itself.
        # self.mock_agent.analyze_image.assert_not_called()
        
        # 5. Check that the metadata from the agent was correctly parsed
        self.assertEqual(result_document["metadata"]["title"], "Mock Title")
        self.assertIn("Author A", result_document["metadata"]["authors"])

if __name__ == '__main__':
    unittest.main()
