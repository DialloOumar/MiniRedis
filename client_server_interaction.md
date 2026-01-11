# Client-Server Interaction Sequence Diagram

This document explains how the MiniRedis client and server interact through the RESP protocol over network sockets.

## Sequence Diagram

```
Client                    Network Socket              Server                  ProtocolHandler
  |                            |                         |                            |
  |--connect()---------------->|                         |                            |
  |    (creates TCP socket)    |                         |                            |
  |                            |                         |                            |
  |--execute("SET","key","val")|                         |                            |
  |                            |                         |                            |
  | Convert to list:           |                         |                            |
  | ["SET", "key", "val"]      |                         |                            |
  |                            |                         |                            |
  | write_response()---------->|                         |                            |
  |   (encodes to RESP)        |                         |                            |
  |   *3\r\n$3\r\nSET\r\n...   |                         |                            |
  |                            |--bytes over network---->|                            |
  |                            |                         |                            |
  |                            |                         | connection_handler()       |
  |                            |                         |   (while loop running)     |
  |                            |                         |                            |
  |                            |                         |--handle_request()--------->|
  |                            |                         |                            |
  |                            |                         |                            | read first byte: '*'
  |                            |                         |                            | handle_array()
  |                            |                         |                            | reads: ["SET","key","val"]
  |                            |                         |                            |
  |                            |                         |<--returns data-------------|
  |                            |                         |   ["SET", "key", "val"]    |
  |                            |                         |                            |
  |                            |                         | get_response(data)         |
  |                            |                         |   command = "SET"          |
  |                            |                         |   _kv["key"] = "val"       |
  |                            |                         |   return "OK"              |
  |                            |                         |                            |
  |                            |                         |--write_response("OK")----->|
  |                            |                         |                            |
  |                            |                         |                            | encode to RESP:
  |                            |                         |                            | $2\r\nOK\r\n
  |                            |                         |                            |
  |                            |<--bytes over network------------------------write---|
  |                            |   $2\r\nOK\r\n          |                            |
  |                            |                         |                            |
  | handle_request()<----------|                         |                            |
  |   (decodes RESP)           |                         |                            |
  |   reads: "OK"              |                         |                            |
  |                            |                         |                            |
  | return "OK"                |                         | (loop continues,           |
  |<--returns to caller        |                         |  waits for next command)   |
  |                            |                         |                            |
  |                            |                         |                            |
  |--execute("GET", "key")-----|                         |                            |
  |                            |                         |                            |
  | write_response()---------->|                         |                            |
  |   *2\r\n$3\r\nGET\r\n...   |                         |                            |
  |                            |--bytes over network---->|                            |
  |                            |                         |                            |
  |                            |                         |--handle_request()--------->|
  |                            |                         |                            | reads: ["GET", "key"]
  |                            |                         |<--returns------------------|
  |                            |                         |                            |
  |                            |                         | get_response(data)         |
  |                            |                         |   return _kv["key"]        |
  |                            |                         |   returns "val"            |
  |                            |                         |                            |
  |                            |                         |--write_response("val")---->|
  |                            |                         |                            | encode: $3\r\nval\r\n
  |                            |<--bytes over network------------------------write---|
  |                            |                         |                            |
  | handle_request()<----------|                         |                            |
  |   reads: "val"             |                         |                            |
  |                            |                         |                            |
  | return "val"               |                         |                            |
  |                            |                         |                            |
  |--disconnect()------------->|                         |                            |
  |   (closes socket)          |                         |                            |
  |                            |---connection closed---->|                            |
  |                            |                         |                            |
  |                            |                         | handle_request()           |
  |                            |                         |   read(1) returns empty    |
  |                            |                         |   raises Disconnect        |
  |                            |                         |                            |
  |                            |                         | except Disconnect:         |
  |                            |                         |   break (exit loop)        |
  |                            |                         |                            |
  |                            |                         | connection_handler ends    |
```

## Component Descriptions

### Client (client.py)
The client is responsible for:
1. **Connecting** - Creates TCP socket and connects to server
2. **Encoding** - Converts Python commands to RESP format using `write_response()`
3. **Sending** - Transmits encoded bytes over network socket
4. **Receiving** - Reads response bytes from socket
5. **Decoding** - Converts RESP response to Python objects using `handle_request()`

**Key Methods:**
- `connect()` - Establishes TCP connection and creates socket file object
- `execute(*args)` - Sends command and waits for response
- `disconnect()` - Closes socket connection

### Server (server.py)
The server is responsible for:
1. **Listening** - Waits for client connections on specified port
2. **Connection Handling** - Spawns handler for each client connection
3. **Request Processing** - Runs infinite loop reading commands
4. **Command Execution** - Processes commands through `get_response()`
5. **Response Sending** - Encodes and sends responses back to client

**Key Methods:**
- `run()` - Starts server listening on port 31337
- `connection_handler()` - Handles individual client connection in while loop
- `get_response()` - Executes commands (GET, SET, DELETE, PING)

### ProtocolHandler (protocalhandler.py)
**Shared component** used by both client and server for RESP protocol handling.

**Reading (Decoding):**
- `handle_request()` - Entry point, reads first byte and dispatches
- `handle_simple_string()` - Decodes `+OK\r\n`
- `handle_error()` - Decodes `-Error message\r\n`
- `handle_integer()` - Decodes `:123\r\n`
- `handle_bulk_string()` - Decodes `$5\r\nhello\r\n`
- `handle_array()` - Decodes `*3\r\n...` (recursive for nested arrays)

**Writing (Encoding):**
- `write_response()` - Encodes Python objects to RESP format
  - `int` → `:123\r\n`
  - `str` → `$5\r\nhello\r\n`
  - `list` → `*3\r\n...` (recursive)
  - `Error` → `-Error message\r\n`
  - `None` → `$-1\r\n`

### Network Socket
The socket is a **bidirectional communication channel** that:
- Transmits raw bytes between client and server
- Provides reliable, ordered delivery (TCP)
- Doesn't understand RESP protocol (just bytes)
- Created using Python's `socket` module

## Message Flow Example: SET Command

### Step 1: Client Encodes Command
```python
# Client code
client.execute("SET", "name", "Alice")

# Internal: convert to list
command = ["SET", "name", "Alice"]

# Encode to RESP array
*3\r\n           # Array of 3 elements
$3\r\nSET\r\n    # Bulk string "SET"
$4\r\nname\r\n   # Bulk string "name"
$5\r\nAlice\r\n  # Bulk string "Alice"
```

### Step 2: Bytes Transmitted Over Network
```
Raw bytes: *3\r\n$3\r\nSET\r\n$4\r\nname\r\n$5\r\nAlice\r\n
```

### Step 3: Server Decodes Command
```python
# Server receives bytes and decodes
data = handle_request(socket_file)
# Result: ["SET", "name", "Alice"]
```

### Step 4: Server Executes Command
```python
# Server processes command
resp = get_response(["SET", "name", "Alice"])
# Executes: self._kv["name"] = "Alice"
# Returns: "OK"
```

### Step 5: Server Encodes Response
```python
# Encode response to RESP
write_response(socket_file, "OK")
# Encodes to: $2\r\nOK\r\n
```

### Step 6: Bytes Transmitted Back
```
Raw bytes: $2\r\nOK\r\n
```

### Step 7: Client Decodes Response
```python
# Client receives and decodes
resp = handle_request(socket_file)
# Result: "OK"
# Returns to caller
```

## Key Concepts

### 1. Protocol Symmetry
Both client and server use the **same ProtocolHandler** class:
- Client: Encodes commands (write) → Decodes responses (read)
- Server: Decodes commands (read) → Encodes responses (write)

### 2. Request-Response Pattern
- Client sends ONE command
- Server sends ONE response
- Client waits for response before sending next command
- Server waits for next command after sending response

### 3. Connection Lifecycle
```
Client connects → Server accepts → Multiple request/response cycles → Client disconnects
```

### 4. Error Handling
- **Protocol errors**: Invalid RESP format → raises exception
- **Command errors**: Unknown command, wrong args → returns Error object
- **Disconnect**: Client closes connection → server catches Disconnect exception

### 5. Concurrency
- Server can handle **multiple clients** simultaneously (gevent)
- Each client gets its own `connection_handler()` running in parallel
- Separate key-value store is shared (needs locking for production)

## Data Flow Summary

```
Python Object (Client)
    ↓
RESP Encoding (ProtocolHandler)
    ↓
Bytes (Network Socket)
    ↓
RESP Decoding (ProtocolHandler)
    ↓
Python Object (Server)
    ↓
Command Execution (Server.get_response)
    ↓
Python Object (Response)
    ↓
RESP Encoding (ProtocolHandler)
    ↓
Bytes (Network Socket)
    ↓
RESP Decoding (ProtocolHandler)
    ↓
Python Object (Client)
```

## Files Reference

- **client.py** - Client implementation with socket connection
- **server.py** - Server implementation with connection handling
- **protocalhandler.py** - Shared RESP protocol encoding/decoding
- **test_protocol.py** - Unit tests for protocol parsing (19 tests)
- **test_writer.py** - Unit tests for protocol writing (10 tests)
- **test_server.py** - Unit tests for command execution (20 tests)

## Architecture Benefits

1. **Separation of Concerns**
   - Protocol layer (ProtocolHandler) is independent
   - Business logic (Server.get_response) is separate
   - Network handling is isolated

2. **Reusability**
   - Same ProtocolHandler for client and server
   - Can be used for testing without network

3. **Testability**
   - Each component can be tested independently
   - Protocol tests use BytesIO (no network needed)
   - Server tests call get_response() directly

4. **Maintainability**
   - Clear boundaries between components
   - Easy to add new commands or data types
   - Protocol changes don't affect business logic
