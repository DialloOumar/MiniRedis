import unittest
from io import BytesIO
from server import ProtocolHandler, Error


class TestWriteResponse(unittest.TestCase):
    """Unit tests for write_response method"""

    def setUp(self):
        """This runs before each test"""
        self.handler = ProtocolHandler()

    def test_write_integer(self):
        """Test writing an integer"""
        output = BytesIO()
        self.handler.write_response(output, 42)
        self.assertEqual(output.getvalue(), b':42\r\n')

    def test_write_string(self):
        """Test writing a string as bulk string"""
        output = BytesIO()
        self.handler.write_response(output, "foobar")
        self.assertEqual(output.getvalue(), b'$6\r\nfoobar\r\n')

    def test_write_empty_string(self):
        """Test writing an empty string"""
        output = BytesIO()
        self.handler.write_response(output, "")
        self.assertEqual(output.getvalue(), b'$0\r\n\r\n')

    def test_write_error(self):
        """Test writing an error"""
        output = BytesIO()
        self.handler.write_response(output, Error("ERR unknown command"))
        self.assertEqual(output.getvalue(), b'-ERR unknown command\r\n')

    def test_write_none(self):
        """Test writing None (null bulk string)"""
        output = BytesIO()
        self.handler.write_response(output, None)
        self.assertEqual(output.getvalue(), b'$-1\r\n')

    def test_write_empty_array(self):
        """Test writing an empty array"""
        output = BytesIO()
        self.handler.write_response(output, [])
        self.assertEqual(output.getvalue(), b'*0\r\n')

    def test_write_array_strings(self):
        """Test writing array of strings"""
        output = BytesIO()
        self.handler.write_response(output, ['foo', 'bar'])
        self.assertEqual(output.getvalue(), b'*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')

    def test_write_array_mixed(self):
        """Test writing array with mixed types"""
        output = BytesIO()
        self.handler.write_response(output, [1, 'hello', 42])
        self.assertEqual(output.getvalue(), b'*3\r\n:1\r\n$5\r\nhello\r\n:42\r\n')

    def test_write_nested_array(self):
        """Test writing nested array"""
        output = BytesIO()
        self.handler.write_response(output, [['foo'], 'bar'])
        self.assertEqual(output.getvalue(), b'*2\r\n*1\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')

    def test_write_string_with_newline(self):
        """Test writing string containing newlines"""
        output = BytesIO()
        self.handler.write_response(output, 'Hello\r\nWorld')
        self.assertEqual(output.getvalue(), b'$12\r\nHello\r\nWorld\r\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
