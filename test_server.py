import unittest
from server import Server, CommandError, Error


class TestServerCommands(unittest.TestCase):
    """Unit tests for Server.get_response() command execution"""

    def setUp(self):
        """This runs before each test - creates a fresh server"""
        self.server = Server()

    def test_ping_command(self):
        """Test PING command returns PONG"""
        result = self.server.get_response(['PING'])
        self.assertEqual(result, 'PONG')

    def test_ping_lowercase(self):
        """Test PING command is case insensitive"""
        result = self.server.get_response(['ping'])
        self.assertEqual(result, 'PONG')

    def test_ping_wrong_args(self):
        """Test PING with arguments raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['PING', 'extra'])
        self.assertIn('Wrong number of arguments', str(context.exception))

    def test_set_command(self):
        """Test SET command stores value"""
        result = self.server.get_response(['SET', 'mykey', 'myvalue'])
        self.assertEqual(result, 'OK')
        # Verify it was actually stored
        self.assertEqual(self.server._kv['mykey'], 'myvalue')

    def test_set_wrong_args_too_few(self):
        """Test SET with too few arguments raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['SET', 'key'])
        self.assertIn('Wrong number of arguments for SET', str(context.exception))

    def test_set_wrong_args_too_many(self):
        """Test SET with too many arguments raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['SET', 'key', 'value', 'extra'])
        self.assertIn('Wrong number of arguments for SET', str(context.exception))

    def test_get_existing_key(self):
        """Test GET command retrieves stored value"""
        # First store a value
        self.server._kv['testkey'] = 'testvalue'
        # Then retrieve it
        result = self.server.get_response(['GET', 'testkey'])
        self.assertEqual(result, 'testvalue')

    def test_get_nonexistent_key(self):
        """Test GET command returns None for missing key"""
        result = self.server.get_response(['GET', 'nonexistent'])
        self.assertIsNone(result)

    def test_get_wrong_args(self):
        """Test GET with wrong number of arguments raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['GET'])
        self.assertIn('Wrong number of arguments for GET', str(context.exception))

    def test_delete_existing_key(self):
        """Test DELETE removes existing key and returns 1"""
        # First store a value
        self.server._kv['deletekey'] = 'value'
        # Then delete it
        result = self.server.get_response(['DELETE', 'deletekey'])
        self.assertEqual(result, 1)
        # Verify it's gone
        self.assertNotIn('deletekey', self.server._kv)

    def test_delete_nonexistent_key(self):
        """Test DELETE on nonexistent key returns 0"""
        result = self.server.get_response(['DELETE', 'nonexistent'])
        self.assertEqual(result, 0)

    def test_delete_wrong_args(self):
        """Test DELETE with wrong number of arguments raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['DELETE'])
        self.assertIn('Wrong number of arguments for DELETE', str(context.exception))

    def test_unknown_command(self):
        """Test unknown command raises error"""
        with self.assertRaises(CommandError) as context:
            self.server.get_response(['UNKNOWN', 'arg'])
        self.assertIn('Unknown command', str(context.exception))
        self.assertIn('UNKNOWN', str(context.exception))

    def test_set_then_get(self):
        """Test SET followed by GET workflow"""
        # SET a value
        set_result = self.server.get_response(['SET', 'workflow', 'test'])
        self.assertEqual(set_result, 'OK')
        # GET the value
        get_result = self.server.get_response(['GET', 'workflow'])
        self.assertEqual(get_result, 'test')

    def test_set_overwrites_existing(self):
        """Test SET overwrites existing value"""
        self.server.get_response(['SET', 'key', 'old'])
        self.server.get_response(['SET', 'key', 'new'])
        result = self.server.get_response(['GET', 'key'])
        self.assertEqual(result, 'new')

    def test_multiple_keys(self):
        """Test storing and retrieving multiple keys"""
        self.server.get_response(['SET', 'key1', 'value1'])
        self.server.get_response(['SET', 'key2', 'value2'])
        self.server.get_response(['SET', 'key3', 'value3'])

        self.assertEqual(self.server.get_response(['GET', 'key1']), 'value1')
        self.assertEqual(self.server.get_response(['GET', 'key2']), 'value2')
        self.assertEqual(self.server.get_response(['GET', 'key3']), 'value3')


if __name__ == '__main__':
    unittest.main(verbosity=2)
