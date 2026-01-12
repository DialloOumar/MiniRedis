# MiniRedis

A lightweight Redis implementation in Python built for learning purposes.

## Overview

MiniRedis is a simplified Redis clone that implements the RESP (Redis Serialization Protocol) for communication. This project was built to understand networking protocols, concurrent server architecture, and data structure implementations.

## Features Implemented

### ✅ RESP Protocol Parser & Writer

- **Simple Strings** (`+OK\r\n`) - Basic string responses
- **Integers** (`:42\r\n`) - Numeric values
- **Errors** (`-ERR message\r\n`) - Error responses
- **Bulk Strings** (`$6\r\nfoobar\r\n`) - Binary-safe strings with length prefix
- **Arrays** (`*2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n`) - Collections of any RESP type, including nested arrays
- **Bidirectional encoding/decoding** - Parse incoming RESP and encode outgoing responses

### ✅ Command Execution

- **GET** - Retrieve values from key-value store
- **SET** - Store key-value pairs
- **DELETE** - Remove keys from store
- **PING** - Health check command
- **Argument validation** - Proper error handling for invalid commands
- **Case-insensitive commands** - Works with uppercase or lowercase

### ✅ Server & Client

- **Gevent-based server** - Handles concurrent client connections
- **Python client** - Socket-based client for programmatic access
- **Connection management** - Proper connect/disconnect handling
- **Request-response cycle** - Multiple commands per connection

## Architecture

```
┌─────────────────────────────────────────┐
│           Client Connection             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         ProtocolHandler                 │
│  - Parse RESP commands                  │
│  - Encode RESP responses                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         Server (gevent-based)           │
│  - Handle connections                   │
│  - Execute commands                     │
│  - Manage key-value store               │
└─────────────────────────────────────────┘
```

## Project Structure

```
MiniRedis/
├── server.py                      # Server implementation with connection handling
├── client.py                      # Redis client for programmatic access
├── protocalhandler.py             # RESP protocol parser and writer
├── test_protocol.py               # Unit tests for RESP parsing (19 tests)
├── test_writer.py                 # Unit tests for RESP encoding (10 tests)
├── test_server.py                 # Unit tests for command execution (20 tests)
├── test_integration.py            # End-to-end integration tests
├── client_server_interaction.md   # Sequence diagram and architecture docs
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

1. Clone the repository
2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install gevent
   ```

## Usage

### Starting the Server

```python
from server import Server

server = Server()
server.run()  # Starts listening on 127.0.0.1:31337
```

### Using the Client

```python
from client import Client

# Connect to server
client = Client()
client.connect()

# Execute commands
client.execute("PING")                    # Returns "PONG"
client.execute("SET", "name", "Alice")    # Returns "OK"
client.execute("GET", "name")             # Returns "Alice"
client.execute("DELETE", "name")          # Returns 1

# Disconnect
client.disconnect()
```

## Running Tests

Run all tests:

```bash
# Protocol parsing tests (19 tests)
python test_protocol.py

# Protocol writing tests (10 tests)
python test_writer.py

# Server command tests (20 tests)
python test_server.py

# Integration tests (requires server running)
python test_integration.py
```

Expected output:

```
Ran 49 tests in 0.003s

OK
```

## RESP Protocol Examples

### Simple String

```
Input:  +OK\r\n
Output: "OK"
```

### Bulk String

```
Input:  $6\r\nfoobar\r\n
Output: "foobar"
```

### Array (Redis Command)

```
Input:  *2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n
Output: ["GET", "mykey"]
```

### Nested Array

```
Input:  *2\r\n*1\r\n$3\r\nfoo\r\n$3\r\nbar\r\n
Output: [["foo"], "bar"]
```

## Learning Objectives

This project demonstrates understanding of:

- **Network Protocol Parsing**: Implementing a wire protocol from specification
- **Binary-Safe Data Handling**: Working with bytes vs strings
- **Recursion**: Parsing nested data structures
- **Concurrency**: Using gevent for handling multiple clients
- **Test-Driven Development**: Writing comprehensive unit tests
- **Error Handling**: Graceful handling of malformed input and edge cases

## Technical Details

### Protocol Handler

The `ProtocolHandler` class uses a dispatcher pattern:

1. Read first byte to identify data type
2. Dispatch to appropriate handler method
3. Recursively parse complex types (arrays)
4. Return parsed Python objects

### Key Design Decisions

- **BytesIO for testing**: Allows unit testing protocol parsing without network I/O
- **Gevent for concurrency**: Lightweight greenlet-based concurrency
- **Separation of concerns**: Protocol parsing separate from command execution

## Testing

The test suite covers:

- All RESP data types
- Edge cases (empty strings, null values, zero)
- Binary-safe data (strings containing `\r\n`)
- Nested structures
- Error conditions (disconnection, malformed data)

## Roadmap: Future Enhancements

### Phase 1: Persistence Layer (Weeks 1-2) 🎯 PRIORITY

**Why:** Learn data durability, file I/O, and crash recovery - fundamental backend skills.

#### AOF (Append-Only File)

- [ ] **Basic AOF Implementation**

  - [ ] Log every write command (SET, DELETE) to appendonly.aof
  - [ ] Replay log on server startup to restore state
  - [ ] Handle file I/O errors gracefully

- [ ] **Fsync Control**

  - [ ] Implement fsync policies (always, everysec, no)
  - [ ] Add configuration for sync frequency
  - [ ] Benchmark performance vs durability trade-offs

- [ ] **AOF Rewrite**

  - [ ] Background task to compress AOF log
  - [ ] Remove redundant commands (e.g., SET key1 a; SET key1 b → SET key1 b)
  - [ ] Atomic AOF file replacement

- [ ] **Crash Recovery**
  - [ ] Handle truncated/corrupted AOF files
  - [ ] Validate commands during replay
  - [ ] Log errors and continue with valid commands

#### RDB Snapshots (Optional)

- [ ] Periodic full database snapshots
- [ ] Binary serialization (pickle or custom format)
- [ ] Background snapshotting without blocking server
- [ ] Load RDB on startup if AOF not available

**Learning Outcomes:** Write-ahead logging, durability guarantees, background tasks, crash recovery

---

### Phase 2: REST API Layer (Weeks 3-4)

**Why:** Most backend jobs involve building REST APIs - make MiniRedis accessible via HTTP.

- [ ] **Flask/FastAPI Wrapper**

  - [ ] `GET /keys/{key}` - Retrieve value
  - [ ] `POST /keys` - Set key-value (JSON body)
  - [ ] `DELETE /keys/{key}` - Remove key
  - [ ] `GET /health` - Server health check

- [ ] **API Features**

  - [ ] Proper HTTP status codes (200, 404, 500)
  - [ ] JSON request/response format
  - [ ] Error handling and validation
  - [ ] API documentation (Swagger/OpenAPI)

- [ ] **Connection Pooling**
  - [ ] Reuse client connections
  - [ ] Max connection limits
  - [ ] Connection timeout handling

**Learning Outcomes:** REST API design, HTTP methods, JSON serialization, connection pooling

---

### Phase 3: Security & Authentication (Weeks 5-6)

**Why:** Production systems need authentication and authorization.

- [ ] **Authentication**

  - [ ] AUTH command for password verification
  - [ ] Password hashing (bcrypt/argon2)
  - [ ] Session management
  - [ ] JWT token support for HTTP API

- [ ] **Authorization**

  - [ ] User roles (admin, read-only, read-write)
  - [ ] Per-key access control
  - [ ] Command whitelisting/blacklisting

- [ ] **Security Hardening**
  - [ ] Rate limiting (max commands/sec per client)
  - [ ] Input validation and sanitization
  - [ ] Command injection prevention
  - [ ] TLS/SSL support for encrypted connections

**Learning Outcomes:** Authentication patterns, password security, authorization models, rate limiting

---

### Phase 4: Advanced Data Structures (Weeks 7-8)

**Why:** Learn different data structure implementations and their use cases.

- [ ] **Lists**

  - [ ] LPUSH/RPUSH - Push to left/right
  - [ ] LPOP/RPOP - Pop from left/right
  - [ ] LRANGE - Get range of elements
  - [ ] LLEN - Get list length

- [ ] **Hashes**

  - [ ] HSET/HGET - Set/get hash field
  - [ ] HDEL - Delete hash field
  - [ ] HGETALL - Get all fields and values
  - [ ] HLEN - Get number of fields

- [ ] **Sets**

  - [ ] SADD/SREM - Add/remove members
  - [ ] SMEMBERS - Get all members
  - [ ] SISMEMBER - Check membership
  - [ ] SINTER/SUNION - Set operations

- [ ] **Sorted Sets**
  - [ ] ZADD - Add with score
  - [ ] ZRANGE - Get range by rank
  - [ ] ZRANGEBYSCORE - Get range by score
  - [ ] ZREM - Remove member

**Learning Outcomes:** Data structure implementations, algorithmic complexity, memory efficiency

---

### Phase 5: Monitoring & Observability (Week 9)

**Why:** Production systems need metrics, logging, and debugging capabilities.

- [ ] **Metrics & Stats**

  - [ ] INFO command - Server stats (uptime, memory, connections)
  - [ ] Commands executed counter
  - [ ] Requests per second tracking
  - [ ] Memory usage monitoring

- [ ] **Logging**

  - [ ] Structured logging (JSON format)
  - [ ] Log levels (DEBUG, INFO, WARNING, ERROR)
  - [ ] Command audit log
  - [ ] Slow query logging

- [ ] **Monitoring Endpoints**
  - [ ] Prometheus metrics export
  - [ ] Health check endpoint
  - [ ] Ready/liveness probes for Kubernetes

**Learning Outcomes:** Observability patterns, metrics collection, structured logging, monitoring

---

### Phase 6: Performance & Scalability (Week 10)

**Why:** Learn how to optimize and benchmark backend systems.

- [ ] **Performance Optimization**

  - [ ] Profile memory usage
  - [ ] Benchmark commands/second throughput
  - [ ] Optimize hot code paths
  - [ ] Memory-efficient data structures

- [ ] **Load Testing**

  - [ ] Concurrent client stress tests
  - [ ] Latency percentiles (p50, p95, p99)
  - [ ] Memory leak detection
  - [ ] Connection limit testing

- [ ] **Scalability Features**
  - [ ] Connection pooling and reuse
  - [ ] Multi-threaded/async request handling
  - [ ] Memory eviction policies (LRU, LFU)
  - [ ] Max memory limits

**Learning Outcomes:** Performance profiling, load testing, optimization techniques, scalability patterns

---

### Phase 7: Advanced Features (Week 11+)

**Why:** Learn distributed systems concepts and advanced Redis features.

- [ ] **Key Expiration**

  - [ ] EXPIRE/TTL commands
  - [ ] Background expiration cleanup
  - [ ] Lazy deletion on access

- [ ] **Pub/Sub**

  - [ ] PUBLISH/SUBSCRIBE messaging
  - [ ] Channel pattern matching
  - [ ] Message broadcasting

- [ ] **Transactions**

  - [ ] MULTI/EXEC command batching
  - [ ] WATCH for optimistic locking
  - [ ] Rollback on errors

- [ ] **Replication** (Advanced)

  - [ ] Master-slave replication
  - [ ] Command propagation
  - [ ] Sync and async replication modes

- [ ] **Clustering** (Advanced)
  - [ ] Hash slot distribution
  - [ ] Cluster node discovery
  - [ ] Automatic failover

**Learning Outcomes:** Distributed systems, replication, consistency models, cluster management

---

### Testing & Quality (Ongoing)

- [ ] Unit tests for each feature (maintain >80% coverage)
- [ ] Integration tests for client-server interaction
- [ ] Load tests and performance benchmarks
- [ ] Documentation updates for each feature
- [ ] Code reviews and refactoring

---

## Resources

- [Redis Protocol Specification (RESP)](https://redis.io/docs/reference/protocol-spec/)
- [Redis Commands](https://redis.io/commands/)

## License

This is a learning project - feel free to use and modify as needed.

## Author

Built as a hands-on learning project to understand Redis internals and network protocol implementation.
