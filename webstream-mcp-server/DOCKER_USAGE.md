# Docker Usage Guide for WebstreamMCP

## Quick Start with Docker Compose

### 1. Start the Container

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Start the container in detached mode
- Keep it running until you stop it
- Expose port 8000 for the web interface

### 2. View Logs

```bash
docker-compose logs -f
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

You'll see a live dashboard where events will appear when pushed through the MCP server.

### 4. Send Messages to the MCP Server

You can interact with the MCP server via stdin using docker exec:

```bash
# List available tools
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | docker exec -i webstream-mcp-server python webstream_server.py

# Push a message to the stream (requires the server to be running with the push_stream tool)
# Note: This is typically done through Claude Desktop, not directly
```

### 5. Connect to the Stream from Your Application

#### JavaScript/Node.js
```javascript
const eventSource = new EventSource('http://localhost:8000/stream');
eventSource.onmessage = (event) => {
    console.log('Received:', event.data);
};
```

#### Python
```python
import requests
import sseclient

response = requests.get('http://localhost:8000/stream', stream=True)
client = sseclient.SSEClient(response)
for event in client.events():
    print(f'Received: {event.data}')
```

#### cURL (for testing)
```bash
curl -N http://localhost:8000/stream
```

### 6. Stop the Container

```bash
docker-compose down
```

## Configuration

### Change Port

Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "9000:8000"  # Host port 9000 -> Container port 8000
```

### Enable Development Mode

Uncomment the volume mount in `docker-compose.yml` to see live changes:
```yaml
volumes:
  - ./webstream_server.py:/app/webstream_server.py
```

Then restart the container:
```bash
docker-compose restart
```

## Useful Commands

```bash
# Rebuild the image
docker-compose build

# Start and rebuild
docker-compose up -d --build

# View running containers
docker-compose ps

# Execute commands in the container
docker-compose exec webstream-mcp bash

# View resource usage
docker stats webstream-mcp-server

# Remove everything (including volumes)
docker-compose down -v
```

## Integration with Claude Desktop

When using this with Claude Desktop and Docker MCP Gateway:

1. Keep this container running with `docker-compose up -d`
2. Configure your MCP gateway to point to this container
3. Ask Claude to "Push a message to the webstream"
4. Watch the message appear on http://localhost:8000

## Troubleshooting

### Container exits immediately
- Check logs: `docker-compose logs`
- Verify the `stdin_open: true` and `tty: true` are set in docker-compose.yml

### Can't access port 8000
- Verify container is running: `docker-compose ps`
- Check port isn't already in use: `lsof -i :8000` (macOS/Linux)
- Try a different port mapping in docker-compose.yml

### No messages appearing on the stream
- Ensure the web server started: Check logs for "Web server started"
- Connect to http://localhost:8000/stream first
- Then trigger the push_stream tool through Claude
- Messages are only pushed when clients are connected

### Healthcheck failing
- The healthcheck verifies port 8000 is accessible
- Check logs for web server startup errors
- The server starts on-demand when push_stream is called

## Architecture

```
Your LLM (Claude) 
    ↓
MCP Gateway (Docker MCP)
    ↓
WebstreamMCP Server (This Container)
    ↓
Web Server (Port 8000)
    ↓
SSE Stream Endpoint (/stream)
    ↓
Your Applications/Browsers
```

