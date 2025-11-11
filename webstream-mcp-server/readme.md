# WebstreamMCP Server

A Model Context Protocol (MCP) server that provides a web server with Server-Sent Events (SSE) streaming capability for pushing real-time messages to connected clients.

## Purpose

This MCP server provides a secure interface for AI assistants to push events to a web stream that other applications can listen to via Server-Sent Events (SSE).

## Features

### Current Implementation

- **`push_stream`** - Push messages to all connected web clients via SSE
  - Automatically starts a web server on demand
  - Maintains persistent connections with multiple clients
  - Provides timestamped messages
  - Includes a web interface for testing

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)
- A browser or application that supports EventSource/SSE

## Installation

See the step-by-step instructions provided with the files.

## Usage Examples

In Claude Desktop, you can ask:

- "Push the message 'Hello World' to the webstream"
- "Send 'System update completed' to all stream listeners"
- "Broadcast 'New event detected' on port 8080"

### Testing the Stream

1. After pushing a message, open `http://localhost:8000` in your browser
2. You'll see a live dashboard showing all incoming events
3. Use Claude to push more messages and watch them appear in real-time

### Connecting from Code
```javascript
// JavaScript/Node.js
const eventSource = new EventSource('http://localhost:8000/stream');
eventSource.onmessage = (event) => {
    console.log('Received:', event.data);
};
```
```python
# Python
import sseclient
import requests

response = requests.get('http://localhost:8000/stream', stream=True)
client = sseclient.SSEClient(response)
for event in client.events():
    print(f'Received: {event.data}')
```

## Architecture
```
Claude Desktop → MCP Gateway → WebstreamMCP Server → Web Server (aiohttp)
                                                           ↓
                                                     SSE Stream
                                                           ↓
                                              Connected Clients
                                         (Browsers, Apps, Services)
```

## Development

### Local Testing
```bash
# Run directly
python webstream_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python webstream_server.py
```

### Adding New Tools

1. Add the function to `webstream_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## Port Configuration

By default, the web server runs on port 8000. You can specify a different port:
```
Claude: Push "test message" to the stream on port 9000
```

Note: When running in Docker, you may need to expose the port in your Docker configuration.

## Troubleshooting

### Tools Not Appearing

- Verify Docker image built successfully
- Check catalog and registry files
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop

### Web Server Not Accessible

- Check that the port is not already in use
- Verify Docker container networking
- Check firewall settings
- Use `docker ps` to verify container is running

### No Clients Receiving Messages

- Ensure clients are connected to the `/stream` endpoint
- Check browser console for connection errors
- Verify the server URL is correct
- Check that messages are being pushed after clients connect

## Security Considerations

- Server binds to 0.0.0.0 by default (accessible from any interface)
- No authentication implemented (suitable for local/trusted networks)
- Consider adding authentication for production use
- CORS is enabled for all origins by default

## Technical Details

- Uses Server-Sent Events (SSE) for real-time streaming
- Built on aiohttp for async web server
- Maintains persistent connections with clients
- Automatic reconnection support on client side
- Keepalive messages every 30 seconds

## License

MIT License