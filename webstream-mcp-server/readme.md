# WebstreamMCP Server

A Model Context Protocol (MCP) server that provides a web server with Server-Sent Events (SSE) streaming capability for pushing real-time messages to connected clients.

## Purpose

This MCP server provides an interface for AI assistants (Claude Desktop, Cursor) to push events to a web stream that other applications can listen to via Server-Sent Events (SSE).

## Features

### MCP Tool

- **`push_stream`** - Push messages to all connected web clients via SSE
  - Parameters: `message` (required), `port` (optional, default 8000), `host` (optional, default 0.0.0.0)
  - Automatically starts web server if not running
  - Maintains persistent connections with multiple clients
  - Provides timestamped messages
  - Returns status with active client count

### Web Endpoints

- **`GET /`** - Interactive HTML dashboard for viewing events in real-time
- **`GET /stream`** - SSE endpoint for receiving events (EventSource compatible)
- **`POST /api/push`** - HTTP API for pushing messages programmatically
  - Request body: `{"message": "your message here"}`
  - Returns: `{"status": "success", "message": "...", "timestamp": "...", "clients": N}`

### Web Features

- Persistent SSE connections with automatic keepalive (every 30 seconds)
- Real-time dashboard with event counter and connection status
- CORS enabled for cross-origin requests
- Handles multiple concurrent clients

## Prerequisites

- Docker and Docker Compose
- A browser or application that supports EventSource/SSE (for receiving messages)
- Claude Desktop or Cursor (for pushing messages via MCP)

## Installation

### Quick Start

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f
```

For detailed setup instructions, see:
- **`QUICK_SETUP.md`** - 3-minute setup guide for Claude Desktop
- **`DOCKER_USAGE.md`** - Complete Docker configuration guide
- **`CURSOR_INTEGRATION.md`** - Cursor-specific integration guide
- **`CLAUDE_DESKTOP_SETUP.md`** - Detailed Claude Desktop setup
- **`CLAUDE_GATEWAY_SETUP.md`** - Alternative gateway setup

## Usage Examples

### From Claude Desktop or Cursor

Ask the AI assistant:

- "Push the message 'Hello World' to the webstream"
- "Send 'System update completed' to all stream listeners"
- "Broadcast 'New event detected' on port 8080"
- "Push 'Server started' to the webstream"

### Via HTTP API

```bash
# Push a message using curl
curl -X POST http://localhost:8000/api/push \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'
```

```python
# Python example using the test script
python test-push.py
```

### Testing the Stream

1. **Open the web dashboard**: Navigate to `http://localhost:8000` in your browser
2. **Connect a listener**: Run the Node.js listener (see `/webstream-listener` folder)
3. **Push messages**: Use Claude/Cursor or the HTTP API
4. **Watch events appear** in real-time across all connected clients

### Connecting from Code

```javascript
// JavaScript/Node.js
const EventSource = require('eventsource');
const eventSource = new EventSource('http://localhost:8000/stream');

eventSource.onopen = () => {
    console.log('✅ Connected to webstream!');
};

eventSource.onmessage = (event) => {
    console.log('📨 Received:', event.data);
};

eventSource.onerror = (error) => {
    console.error('❌ Connection error:', error);
};
```

```python
# Python with sseclient-py
import sseclient
import requests

response = requests.get('http://localhost:8000/stream', stream=True)
client = sseclient.SSEClient(response)
for event in client.events():
    print(f'📨 Received: {event.data}')
```

```bash
# Simple curl test (press Ctrl+C to stop)
curl -N http://localhost:8000/stream
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ AI Assistant (Claude Desktop / Cursor)                  │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol (stdio)
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Docker Container: webstream-mcp-server                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │ WebstreamMCP Server (Python/FastMCP)              │ │
│  │  - push_stream tool                                │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   ↓                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Web Server (aiohttp) - Port 8000                   │ │
│  │  - GET /           → Dashboard                     │ │
│  │  - GET /stream     → SSE endpoint                  │ │
│  │  - POST /api/push  → HTTP API                      │ │
│  └────────────────┬───────────────────────────────────┘ │
└───────────────────┼─────────────────────────────────────┘
                    │ Server-Sent Events (SSE)
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Browser │ │ Node.js │ │  Other  │
   │Dashboard│ │Listener │ │ Clients │
   └─────────┘ └─────────┘ └─────────┘
```

## Development

### Local Testing Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server directly
python webstream_server.py

# Test MCP protocol (tools/list)
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python webstream_server.py
```

### Testing with Docker

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Test the web interface
open http://localhost:8000  # macOS
# or
xdg-open http://localhost:8000  # Linux

# Test pushing via API
python test-push.py
```

### Adding New MCP Tools

1. Open `webstream_server.py`
2. Add your function with the `@mcp.tool()` decorator:
   ```python
   @mcp.tool()
   async def my_new_tool(param: str) -> str:
       """Description of what this tool does."""
       # Your implementation here
       return "Result"
   ```
3. Rebuild the Docker image: `docker-compose build`
4. Restart the container: `docker-compose restart`
5. Restart Claude Desktop or Cursor to pick up the new tool

### Development Mode

To make live changes without rebuilding:

1. Uncomment the volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./webstream_server.py:/app/webstream_server.py
   ```
2. Restart the container: `docker-compose restart`
3. Changes to `webstream_server.py` will be reflected immediately

## Port Configuration

By default, the web server runs on port 8000. You can:

### Change via MCP Tool Parameter
```
Claude/Cursor: Push "test message" to the stream on port 9000
```

### Change in Docker Compose
Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Host port 9000 → Container port 8000
```

**Note**: If you change the container's internal port, you'll also need to update the `DEFAULT_PORT` in `webstream_server.py`.

## Troubleshooting

### Tools Not Appearing in Claude/Cursor

**Symptoms**: The `push_stream` tool is not available in Claude Desktop or Cursor

**Solutions**:
- Verify Docker container is running: `docker ps | grep webstream-mcp-server`
- Start container if needed: `docker-compose up -d`
- Check your MCP configuration:
  - **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Cursor**: `~/.cursor/mcp.json`
- **Completely restart** the application (Quit, don't just close window)
- Check container logs for errors: `docker-compose logs webstream-mcp-server`

### Web Server Not Accessible

**Symptoms**: Cannot access `http://localhost:8000`

**Solutions**:
- Check container is running: `docker-compose ps`
- Verify port mapping: `docker port webstream-mcp-server`
- Check if port is in use: `lsof -i :8000` (macOS/Linux)
- View container logs: `docker-compose logs -f`
- Try accessing from inside container: `docker exec webstream-mcp-server curl localhost:8000`
- Check firewall settings

### Web Server Starts But No Port 8000

**Symptoms**: Web server shows as started but port isn't accessible

**Cause**: The web server starts in a background thread when the first MCP tool is called

**Solutions**:
- Push a message via Claude/Cursor to initialize the web server
- Or wait for the server to fully initialize (check logs)
- The server auto-starts on container launch

### No Clients Receiving Messages

**Symptoms**: Messages are pushed but clients don't receive them

**Solutions**:
- **Connect clients FIRST**, then push messages (SSE is push-only)
- Verify client is connected to correct endpoint: `http://localhost:8000/stream`
- Check browser console for connection errors (F12)
- Test with curl: `curl -N http://localhost:8000/stream`
- Verify messages are being sent: Check container logs for "Active clients: N"
- If using Node.js, ensure you're using the `eventsource` package

### Container Exits Immediately

**Symptoms**: Container starts then stops immediately

**Solutions**:
- Check logs: `docker-compose logs`
- Verify `stdin_open: true` and `tty: true` are in `docker-compose.yml`
- Check for Python errors in logs
- Ensure all dependencies are installed correctly

### "Address already in use" Error

**Symptoms**: Error binding to port 8000

**Solutions**:
- Stop the existing process: `lsof -i :8000` then `kill <PID>`
- Or use a different port in `docker-compose.yml`
- Or use a different port parameter in the MCP tool call

## Security Considerations

### Current Security Posture

- **Network Binding**: Server binds to `0.0.0.0` by default (accessible from all network interfaces)
- **Authentication**: None implemented - suitable only for local development and trusted networks
- **CORS**: Enabled for all origins (`Access-Control-Allow-Origin: *`)
- **Container Security**: Runs as non-root user (`mcpuser`) in Docker
- **API Access**: `/api/push` endpoint is open to any HTTP client

### Recommendations for Production

1. **Add Authentication**: Implement API key or token-based authentication
2. **Use HTTPS**: Deploy behind a reverse proxy (nginx, Caddy) with TLS
3. **Restrict Binding**: Change host to `127.0.0.1` for localhost-only access
4. **Configure CORS**: Limit allowed origins to trusted domains
5. **Rate Limiting**: Add rate limiting to prevent abuse
6. **Network Isolation**: Use Docker networks to isolate the container

### Example: Restricting to Localhost

Edit `webstream_server.py`:
```python
DEFAULT_HOST = "127.0.0.1"  # Instead of "0.0.0.0"
```

## Technical Details

### Technology Stack

- **MCP Framework**: FastMCP (Python MCP SDK)
- **Web Framework**: aiohttp (async HTTP server)
- **Protocol**: Server-Sent Events (SSE) / EventSource
- **Container**: Docker with Python 3.11-slim
- **Transport**: stdio (for MCP communication)

### Architecture Details

- **Threading Model**: Web server runs in a background thread with its own event loop
- **Connection Management**: Set-based tracking of connected SSE clients
- **Auto-start**: Web server initializes on container startup (port 8000)
- **Graceful Handling**: Disconnected clients are automatically removed
- **Keepalive**: SSE connections send keepalive every 30 seconds
- **Message Format**: Timestamped messages in ISO 8601 format (UTC)

### SSE Message Format

```
data: [2025-11-11T12:34:56.789012+00:00] Your message here\n\n
```

Each message includes:
- `data:` prefix (SSE protocol)
- ISO 8601 timestamp with timezone
- The actual message content
- Double newline delimiter

### Connection Lifecycle

1. Client connects to `/stream`
2. Server sends initial connection message
3. Server adds client to active set
4. Messages are broadcasted to all clients in set
5. Keepalive sent every 30 seconds (`: keepalive\n\n`)
6. On disconnect, client is removed from set

### Performance Characteristics

- **Concurrent Clients**: Supports multiple simultaneous connections (limited by system resources)
- **Message Latency**: Near real-time (typically <100ms)
- **Memory Usage**: Minimal per-client overhead
- **CPU Usage**: Low (event-driven architecture)

## Project Files

- `webstream_server.py` - Main MCP server and web server implementation
- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile` - Container image definition
- `requirements.txt` - Python dependencies
- `test-push.py` - HTTP API testing script
- `QUICK_SETUP.md` - Quick start guide
- `DOCKER_USAGE.md` - Docker documentation
- `CURSOR_INTEGRATION.md` - Cursor setup guide
- `CLAUDE_DESKTOP_SETUP.md` - Claude Desktop setup
- `CLAUDE_GATEWAY_SETUP.md` - Alternative gateway setup

## Related Projects

- **webstream-listener** (Node.js) - Example SSE client for receiving messages
- **flutter_webstream_listener** - Flutter/Dart mobile app example

## License

MIT License