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

    def test_bulk_string_simple(self):
        """Test parsing a simple bulk string"""
        fake_data = BytesIO(b'$6\r\nfoobar\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 'foobar')
        self.assertIsInstance(result, str)

    def test_bulk_string_empty(self):
        """Test parsing an empty bulk string"""
        fake_data = BytesIO(b'$0\r\n\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, '')

    def test_bulk_string_null(self):
        """Test parsing a null bulk string"""
        fake_data = BytesIO(b'$-1\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertIsNone(result)

    def test_bulk_string_with_newline(self):
        """Test parsing bulk string containing newlines"""
        fake_data = BytesIO(b'$12\r\nHello\r\nWorld\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, 'Hello\r\nWorld')

    def test_array_empty(self):
        """Test parsing an empty array"""
        fake_data = BytesIO(b'*0\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_array_null(self):
        """Test parsing a null array"""
        fake_data = BytesIO(b'*-1\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertIsNone(result)

    def test_array_simple(self):
        """Test parsing array with bulk strings"""
        # *2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n
        fake_data = BytesIO(b'*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, ['foo', 'bar'])

    def test_array_get_command(self):
        """Test parsing GET mykey command"""
        # GET mykey = *2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n
        fake_data = BytesIO(b'*2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, ['GET', 'mykey'])

    def test_array_mixed_types(self):
        """Test parsing array with mixed types"""
        # [1, "hello", 42] = *3\r\n:1\r\n$5\r\nhello\r\n:42\r\n
        fake_data = BytesIO(b'*3\r\n:1\r\n$5\r\nhello\r\n:42\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, [1, 'hello', 42])

    def test_array_nested(self):
        """Test parsing nested array"""
        # [["foo"], "bar"] = *2\r\n*1\r\n$3\r\nfoo\r\n$3\r\nbar\r\n
        fake_data = BytesIO(b'*2\r\n*1\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')
        result = self.handler.handle_request(fake_data)
        self.assertEqual(result, [['foo'], 'bar'])


if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)
