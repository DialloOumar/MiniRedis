import unittest
from io import BytesIO
from main import ProtocolHandler, Disconnect, Error


class TestProtocolHandler(unittest.TestCase):
    """Unit tests for the ProtocolHandler class"""

    def setUp(self):
        """This runs before each test - creates a fresh handler"""
        self.handler = ProtocolHandler()

    def test_simple_string(self):
        """Test parsing a simple string"""
        fake_data = BytesIO(b'+OK\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 'OK')
        self.assertIsInstance(result, str)

    def test_simple_string_with_spaces(self):
        """Test parsing a simple string with spaces"""
        fake_data = BytesIO(b'+Hello World\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 'Hello World')

    def test_integer_positive(self):
        """Test parsing a positive integer"""
        fake_data = BytesIO(b':42\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def test_integer_negative(self):
        """Test parsing a negative integer"""
        fake_data = BytesIO(b':-100\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, -100)
        self.assertIsInstance(result, int)

    def test_integer_zero(self):
        """Test parsing zero"""
        fake_data = BytesIO(b':0\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 0)

    def test_disconnect_on_empty_read(self):
        """Test that Disconnect is raised when connection closes"""
        fake_data = BytesIO(b'')  # Empty data simulates closed connection
        with self.assertRaises(Disconnect):
            self.handler.handle_request(fake_data)

    def test_simple_string_empty(self):
        """Test parsing an empty simple string"""
        fake_data = BytesIO(b'+\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, '')

    def test_error_simple(self):
        """Test parsin a simple error"""
        fake_data = BytesIO(b'-Error message\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertIsInstance(result, Error)
        self.assertEqual(result.message, "Error message")
    
    def test_error_redis_style(self):
        """Testing Redis style errors"""
        fake_data = BytesIO(b'-ERR unknown command\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertIsInstance(result, Error)
        self.assertEqual(result.message, "ERR unknown command")


if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)
