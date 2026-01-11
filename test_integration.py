"""
Integration test for MiniRedis client and server
Tests the complete system end-to-end
"""

import time
import threading
from client import Client
from server import Server


def run_server():
    """Start the server in a background thread"""
    server = Server()
    server.run()


def test_client_server():
    """Test client-server communication"""

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(1)

    # Create and connect client
    client = Client()
    print("Connecting to server...")
    client.connect()
    print("Connected!")

    # Test PING
    print("\n--- Testing PING ---")
    result = client.execute("PING")
    print(f"PING -> {result}")
    assert result == "PONG", f"Expected 'PONG', got {result}"

    # Test SET
    print("\n--- Testing SET ---")
    result = client.execute("SET", "name", "Alice")
    print(f"SET name Alice -> {result}")
    assert result == "OK", f"Expected 'OK', got {result}"

    # Test GET existing key
    print("\n--- Testing GET (existing key) ---")
    result = client.execute("GET", "name")
    print(f"GET name -> {result}")
    assert result == "Alice", f"Expected 'Alice', got {result}"

    # Test GET non-existent key
    print("\n--- Testing GET (non-existent key) ---")
    result = client.execute("GET", "nonexistent")
    print(f"GET nonexistent -> {result}")
    assert result is None, f"Expected None, got {result}"

    # Test multiple SET/GET
    print("\n--- Testing multiple keys ---")
    client.execute("SET", "key1", "value1")
    client.execute("SET", "key2", "value2")
    client.execute("SET", "key3", "value3")

    result1 = client.execute("GET", "key1")
    result2 = client.execute("GET", "key2")
    result3 = client.execute("GET", "key3")

    print(f"GET key1 -> {result1}")
    print(f"GET key2 -> {result2}")
    print(f"GET key3 -> {result3}")

    assert result1 == "value1"
    assert result2 == "value2"
    assert result3 == "value3"

    # Test DELETE existing key
    print("\n--- Testing DELETE (existing key) ---")
    result = client.execute("DELETE", "key1")
    print(f"DELETE key1 -> {result}")
    assert result == 1, f"Expected 1, got {result}"

    # Verify key was deleted
    result = client.execute("GET", "key1")
    print(f"GET key1 (after delete) -> {result}")
    assert result is None, f"Expected None, got {result}"

    # Test DELETE non-existent key
    print("\n--- Testing DELETE (non-existent key) ---")
    result = client.execute("DELETE", "nonexistent")
    print(f"DELETE nonexistent -> {result}")
    assert result == 0, f"Expected 0, got {result}"

    # Test case insensitivity
    print("\n--- Testing case insensitivity ---")
    result = client.execute("ping")
    print(f"ping (lowercase) -> {result}")
    assert result == "PONG"

    result = client.execute("set", "testkey", "testvalue")
    print(f"set testkey testvalue -> {result}")
    assert result == "OK"

    result = client.execute("get", "testkey")
    print(f"get testkey -> {result}")
    assert result == "testvalue"

    # Disconnect
    print("\n--- Disconnecting ---")
    client.disconnect()
    print("Disconnected!")

    print("\n" + "="*50)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*50)


if __name__ == "__main__":
    test_client_server()
