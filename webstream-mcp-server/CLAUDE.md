# WebstreamMCP Implementation Guide

## Overview

The WebstreamMCP server provides a simple but powerful interface for pushing real-time events to web clients using Server-Sent Events (SSE). This allows AI assistants to broadcast messages that can be consumed by web applications, monitoring dashboards, or any SSE-compatible client.

## Architecture

### Components

1. **MCP Server** - FastMCP-based server handling Claude Desktop communication
2. **Web Server** - aiohttp-based HTTP server serving SSE streams
3. **Stream Manager** - Manages connected clients and message distribution

### Flow
```
Claude → push_stream tool → Web Server → SSE Stream → Connected Clients
```

## Implementation Details

### Server-Sent Events (SSE)

SSE provides a unidirectional channel from server to clients over HTTP:

- Uses standard HTTP connections
- Automatic reconnection on client side
- Text-based protocol
- Wide browser support

### Client Management

The server maintains a set of active client connections:
- Clients are added when they connect to `/stream`
- Automatic cleanup on disconnect
- Broadcast to all clients simultaneously

### Message Format

Messages follow the SSE protocol:
```
data: [timestamp] message content\n\n
```

The double newline signals the end of an event.

## Usage Patterns

### Simple Broadcasting
```
Claude: Push "deployment completed" to the stream
```

### Status Updates
```
Claude: Send "Processing record 1000/5000" to all listeners
```

### Alert System
```
Claude: Broadcast "ALERT: High CPU usage detected" to the webstream
```

## Extension Ideas

1. **Message Types** - Add event types (info, warning, error)
2. **Channels** - Support multiple streams/channels
3. **Authentication** - Add token-based auth
4. **Message History** - Store recent messages for new clients
5. **Filtering** - Allow clients to filter by message type
6. **Acknowledgments** - Track which clients received messages

## Testing

### Browser Testing

Open `http://localhost:8000` to see the test interface with live updates.

### cURL Testing
```bash
# Connect to stream
curl -N http://localhost:8000/stream

# In another terminal, use Claude to push messages
```

### JavaScript Testing
```javascript
const es = new EventSource('http://localhost:8000/stream');
es.onmessage = (e) => console.log('Event:', e.data);
es.onerror = (e) => console.error('Error:', e);
```

## Performance Considerations

- Each client maintains an open connection
- Memory usage scales with client count
- Consider connection limits for production
- Keepalive messages prevent timeout

## Limitations

- Unidirectional (server to client only)
- Text-based messages only
- No built-in authentication
- No message persistence
- No guaranteed delivery

## Best Practices

1. Keep messages concise and meaningful
2. Include timestamps for debugging
3. Monitor active client count
4. Handle client disconnections gracefully
5. Consider message rate limits
6. Use structured data formats (JSON)

## Troubleshooting Tips

### Clients not receiving messages
- Verify client connects before messages are sent
- Check browser console for errors
- Confirm correct endpoint URL

### High memory usage
- Check for client connection leaks
- Monitor active client count
- Implement connection limits

### Connection drops
- Increase keepalive frequency
- Check network stability
- Review server logs

## Future Enhancements

- WebSocket support for bidirectional communication
- Redis backend for multi-instance deployment
- Message queue integration
- Replay capability for historical events
- Client subscription management
- Rate limiting per client
- Message prioritization

## Security Notes

- Current implementation has no authentication
- All messages are plaintext
- CORS allows any origin
- Suitable for trusted networks only
- Add TLS/SSL for production
- Implement token-based auth if needed