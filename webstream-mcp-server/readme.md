# WebhookMCP Server

A Model Context Protocol (MCP) server that provides webhook delivery capability for pushing messages to registered webhook endpoints.

## Purpose

This MCP server provides an interface for AI assistants (Claude Desktop, Cursor) to push messages to registered webhook URLs via HTTP POST requests. This eliminates the need for persistent connections and allows receivers to operate independently.

## Features

### MCP Tool

- **`push_webhook`** - Push messages to all registered webhooks via HTTP POST
  - Parameters: `message` (required), `port` (optional, default 8000), `host` (optional, default 0.0.0.0)
  - Automatically starts web server if not running
  - Sends to multiple webhooks in parallel
  - Provides timestamped messages
  - Returns status with successful delivery count

### Web Endpoints

- **`GET /`** - Interactive HTML dashboard for managing webhooks
- **`POST /api/register`** - Register a webhook URL
  - Request body: `{"webhook_url": "http://your-server/webhook"}`
  - Returns: `{"status": "success", "webhook_url": "...", "total_webhooks": N}`
- **`POST /api/unregister`** - Unregister a webhook URL
  - Request body: `{"webhook_url": "http://your-server/webhook"}`
  - Returns: `{"status": "success", "webhook_url": "...", "total_webhooks": N}`
- **`GET /api/webhooks`** - List all registered webhooks
  - Returns: `{"webhooks": [...], "total": N}`
- **`POST /api/push`** - HTTP API for pushing messages programmatically
  - Request body: `{"message": "your message here"}`
  - Returns: `{"status": "success", "message": "...", "timestamp": "...", "webhooks_notified": N, "total_webhooks": N}`

### Web Features

- No persistent connections required
- Webhook registration and management dashboard
- Parallel webhook delivery for performance
- CORS enabled for cross-origin requests
- Handles multiple registered webhooks

## Prerequisites

- Docker and Docker Compose
- An HTTP server/application to receive webhook POST requests
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

- "Push the message 'Hello World' to the webhooks"
- "Send 'System update completed' to all registered webhooks"
- "Broadcast 'New event detected' on port 8080"
- "Push 'Server started' to the webhooks"

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

### Testing Webhooks

1. **Open the web dashboard**: Navigate to `http://localhost:8000` in your browser
2. **Start a webhook receiver**: Run the Flutter app (see `/flutter_webstream_listener` folder)
3. **Register your webhook**: The Flutter app auto-registers or use the dashboard
4. **Push messages**: Use Claude/Cursor or the HTTP API
5. **Watch messages arrive** at your webhook endpoint

### Registering Webhooks from Code

```bash
# Register a webhook using curl
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "http://your-server:3000/webhook"}'

# List registered webhooks
curl http://localhost:8000/api/webhooks

# Unregister a webhook
curl -X POST http://localhost:8000/api/unregister \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "http://your-server:3000/webhook"}'
```

```javascript
// JavaScript/Node.js - Creating a webhook receiver
const express = require('express');
const app = express();
app.use(express.json());

app.post('/webhook', (req, res) => {
    const { message, timestamp } = req.body;
    console.log(`📨 Received: [${timestamp}] ${message}`);
    res.json({ status: 'success' });
});

app.listen(3000, () => console.log('Webhook receiver running on port 3000'));
```

```python
# Python Flask webhook receiver
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message')
    timestamp = data.get('timestamp')
    print(f'📨 Received: [{timestamp}] {message}')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=3000)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ AI Assistant (Claude Desktop / Cursor)                  │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol (stdio)
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Docker Container: webhook-mcp-server                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ WebhookMCP Server (Python/FastMCP)                │ │
│  │  - push_webhook tool                               │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   ↓                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Web Server (aiohttp) - Port 8000                   │ │
│  │  - GET  /              → Dashboard                 │ │
│  │  - POST /api/register  → Register webhook          │ │
│  │  - POST /api/push      → Push to webhooks          │ │
│  │  - GET  /api/webhooks  → List webhooks             │ │
│  └────────────────┬───────────────────────────────────┘ │
└───────────────────┼─────────────────────────────────────┘
                    │ HTTP POST (Webhooks)
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Flutter │ │ Node.js │ │  Other  │
   │   App   │ │ Server  │ │Receivers│
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

### No Webhooks Receiving Messages

**Symptoms**: Messages are pushed but webhooks don't receive them

**Solutions**:
- **Register webhooks FIRST** via `/api/register`
- Verify webhook is registered: `curl http://localhost:8000/api/webhooks`
- Check webhook endpoint is accessible from the MCP server
- For localhost receivers, ensure correct IP (10.0.2.2 for Android emulator)
- Check container logs for webhook delivery errors
- Verify webhook endpoint accepts POST requests and returns 200 status
- Test webhook manually: `curl -X POST http://your-webhook/webhook -H "Content-Type: application/json" -d '{"message":"test","timestamp":"2025-01-01T00:00:00Z"}'`

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
- **Web Framework**: aiohttp (async HTTP server and client)
- **Protocol**: HTTP POST (Webhooks)
- **Container**: Docker with Python 3.11-slim
- **Transport**: stdio (for MCP communication)

### Architecture Details

- **Threading Model**: Web server runs in a background thread with its own event loop
- **Webhook Management**: Set-based tracking of registered webhook URLs
- **Auto-start**: Web server initializes on container startup (port 8000)
- **Parallel Delivery**: Webhooks are called in parallel using asyncio.gather
- **Timeout Handling**: 10-second timeout per webhook request
- **Message Format**: JSON payload with timestamped messages in ISO 8601 format (UTC)

### Webhook Payload Format

```json
{
  "message": "Your message here",
  "timestamp": "2025-11-11T12:34:56.789012+00:00"
}
```

Each webhook receives:
- `message`: The actual message content
- `timestamp`: ISO 8601 timestamp with timezone (UTC)

### Webhook Lifecycle

1. Receiver registers webhook URL via `/api/register`
2. Server stores webhook URL in registered set
3. When a message is pushed, server makes HTTP POST to all webhooks
4. Each webhook endpoint responds with success/failure
5. Failed webhooks are logged but kept in registry
6. Receiver can unregister via `/api/unregister`

### Performance Characteristics

- **Concurrent Webhooks**: Supports multiple webhooks with parallel delivery
- **Message Latency**: Depends on webhook endpoint response time (10s timeout)
- **Memory Usage**: Minimal - only stores webhook URLs
- **CPU Usage**: Low (event-driven architecture with parallel requests)

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

- **flutter_webstream_listener** - Flutter/Dart mobile app with webhook receiver
- Other webhook-compatible servers and applications

## License

MIT License