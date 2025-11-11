# WebStream Listener Test Guide

## Quick Start

### 1. Start the Listener

In your terminal, navigate to the webstream-listener directory and run:

```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

You should see output like:
```
🌐 WebstreamMCP Client Starting...
📡 Connecting to: http://localhost:8000/stream

✅ Connected to webstream!
⏳ Waiting for messages...

────────────────────────────────────────────────────────

💡 Press Ctrl+C to stop listening
```

### 2. Test the Connection

Now you have two options to test if messages flow through:

#### Option A: Use the Web Interface

1. Open your browser to `http://localhost:8000`
2. You should see the WebstreamMCP dashboard
3. In another terminal, interact with the MCP server through Claude Desktop
4. Ask Claude: "Push the message 'Hello World' to the webstream"
5. Watch the message appear in both:
   - The web dashboard
   - Your Node.js listener terminal

#### Option B: Test with curl

In a **new terminal window**, send a test message:

```bash
# Connect to the stream endpoint directly
curl -N http://localhost:8000/stream
```

This will show you the raw SSE data. You should see:
```
data: Connected at 2025-11-11T...
```

And keepalive messages every 30 seconds:
```
: keepalive
```

### 3. Send Test Messages via MCP

To actually push messages through the MCP server, you need to:

1. Configure Claude Desktop with the MCP server
2. Ask Claude to push a message:
   - "Push 'Test message 1' to the webstream"
   - "Send 'System ready' to all stream listeners"
   - "Broadcast 'Hello from Claude' to the stream"

### 4. Expected Output

When a message is pushed, your listener should show:

```
📨 Event #1 received at 3:45:30 PM
📝 Data: [2025-11-11T14:45:30.123Z] Test message 1
────────────────────────────────────────────────────────

📨 Event #2 received at 3:45:35 PM
📝 Data: [2025-11-11T14:45:35.456Z] System ready
────────────────────────────────────────────────────────
```

## Troubleshooting

### Connection Failed

If you see:
```
❌ Failed to connect to stream
Make sure the WebstreamMCP server is running on port 8000
```

**Solutions:**
1. Check if the Docker container is running:
   ```bash
   cd /Users/dennis/projects/MCP/webstream-mcp-server
   docker-compose ps
   ```

2. If not running, start it:
   ```bash
   docker-compose up -d
   ```

3. Verify port 8000 is accessible:
   ```bash
   curl http://localhost:8000
   ```

### No Messages Appearing

If connected but no messages appear:

1. The web server starts **on-demand** when `push_stream` is first called
2. Messages are only broadcast to **connected clients**
3. You must connect to the stream **before** pushing messages

**Workflow:**
1. Start listener → connects to stream
2. This triggers the web server to start (if not already running)
3. Push message via Claude → appears in listener

### Testing the Full Pipeline

Here's a complete test sequence:

1. **Terminal 1** - Start MCP server:
   ```bash
   cd /Users/dennis/projects/MCP/webstream-mcp-server
   docker-compose up
   # Keep this running
   ```

2. **Terminal 2** - Start listener:
   ```bash
   cd /Users/dennis/projects/MCP/webstream-listener
   node stream-listener.js
   # Keep this running
   ```

3. **Browser** - Open dashboard:
   ```
   http://localhost:8000
   ```

4. **Claude Desktop** - Push a message:
   ```
   "Push 'Testing the webstream!' to the stream"
   ```

5. **Verify** - Message should appear in:
   - Terminal 2 (Node.js listener) ✓
   - Browser dashboard ✓
   - Docker logs ✓

## Advanced Usage

### Run Listener in Background

To run the listener as a background process:

```bash
# Start in background
node stream-listener.js > listener.log 2>&1 &
echo $! > listener.pid

# View logs
tail -f listener.log

# Stop listener
kill $(cat listener.pid)
rm listener.pid
```

### Multiple Listeners

You can run multiple listeners simultaneously:

```bash
# Terminal 1
node stream-listener.js

# Terminal 2
node stream-listener.js

# Both will receive the same messages!
```

### Custom Event Handling

You can modify `stream-listener.js` to process events:

```javascript
eventSource.onmessage = (event) => {
    const data = event.data;
    
    // Parse the message
    if (data.includes('ERROR')) {
        console.error('🚨 Error event:', data);
        // Send alert, log to file, etc.
    } else if (data.includes('SUCCESS')) {
        console.log('✅ Success event:', data);
        // Update dashboard, send notification, etc.
    }
    
    // Store to database, forward to another service, etc.
};
```

## Architecture

```
Claude Desktop
    ↓
    ↓ push_stream tool
    ↓
WebstreamMCP Server (Docker)
    ↓
    ↓ Port 8000
    ↓
    ├─→ /stream endpoint (SSE)
    │       ↓
    │       ├─→ Your Node.js Listener ✓
    │       ├─→ Web Dashboard ✓
    │       └─→ Any other SSE client ✓
    │
    └─→ / endpoint (Web UI)
```

## Performance Notes

- The listener automatically reconnects if disconnected
- Keepalive messages are sent every 30 seconds to maintain the connection
- The EventSource API is designed for long-running connections
- Each listener maintains its own independent connection
- No polling required - true push notifications via SSE

## Security Considerations

- Currently configured for localhost only
- No authentication implemented
- Suitable for local development and testing
- For production use, consider:
  - Authentication tokens
  - HTTPS/TLS encryption
  - Rate limiting
  - Access control lists

