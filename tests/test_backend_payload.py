import unittest
from unittest.mock import MagicMock, patch
from backend import DocumentProcessor, FieldDefinition, FieldType

class TestDocumentProcessor(unittest.TestCase):
    @patch('backend.OpenAI')
    def test_extract_data_payload(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = mock_completion
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.parsed.model_dump.return_value = {}

        # Initialize processor
        processor = DocumentProcessor(api_key="fake_key")

        # Test data
        file_bytes_list = [b"image1", b"image2", b"image3"]
        fields = [FieldDefinition(name="test", description="test", data_type=FieldType.STRING)]

        # Run extraction
        processor.extract_data(file_bytes_list, "png", fields)

        # Verify call arguments
        call_args = mock_client.beta.chat.completions.parse.call_args
        _, kwargs = call_args
        messages = kwargs['messages']
        
        # Check user message content
        user_content = messages[1]['content']
        
        # Expect 1 text block + 3 image blocks
        self.assertEqual(len(user_content), 4)
        self.assertEqual(user_content[0]['type'], 'text')
        self.assertEqual(user_content[1]['type'], 'image_url')
        self.assertEqual(user_content[2]['type'], 'image_url')
        self.assertEqual(user_content[3]['type'], 'image_url')

if __name__ == '__main__':
    unittest.main()
