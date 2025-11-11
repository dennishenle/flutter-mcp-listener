# Cursor Integration Guide for WebstreamMCP

## Current Status

✅ Docker container running  
✅ Web server accessible on port 8000  
✅ Stream endpoint ready at /stream  
✅ MCP server configured in Cursor  

## Configuration

Your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
"WebstreamMCP": {
    "command": "docker",
    "args": [
        "exec",
        "-i",
        "webstream-mcp-server",
        "python",
        "/app/webstream_server.py"
    ]
}
```

## Usage with Cursor

### Step 1: Restart Cursor

The MCP configuration is loaded on startup, so you need to:
1. Completely quit Cursor
2. Reopen Cursor
3. The WebstreamMCP server should now be available

### Step 2: Verify MCP Tools are Available

In Cursor's chat, you can check available tools. The `push_stream` tool should appear from WebstreamMCP.

### Step 3: Push Messages

Ask Cursor's AI:

```
"Push the message 'Hello from Cursor!' to the webstream"
```

or

```
"Send 'Test message' to all webstream listeners"
```

or

```
"Broadcast 'System ready' on the stream"
```

### Step 4: View Messages

Messages will appear in:
- **Browser**: http://localhost:8000
- **Your Node.js listener**: `node stream-listener.js`
- **Any other SSE client** connected to the stream

## Testing the Setup

### Test 1: Verify Web Server

```bash
curl http://localhost:8000
```

Should return HTML dashboard.

### Test 2: Verify Stream Endpoint

```bash
curl -N http://localhost:8000/stream
```

Should show:
```
data: Connected at 2025-11-11T...
: keepalive
```

### Test 3: Start Your Listener

```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

Should show:
```
✅ Connected to webstream!
⏳ Waiting for messages...
```

### Test 4: View in Browser

Open: http://localhost:8000

You should see the WebstreamMCP Event Stream dashboard.

## Known Limitations

### Stdio Transport Issue

The current MCP server uses stdio transport, which means:
- Each `docker exec` starts a new process
- The new process tries to bind to port 8000 (already in use)
- Messages can only be pushed through the persistent Cursor connection

### Workaround for Manual Testing

If you want to test message pushing manually without Cursor, you would need to:
1. Add an HTTP API endpoint to the web server
2. Or use a different architecture (see Alternative Architecture below)

## Alternative Architecture (For Future Enhancement)

To support both Cursor MCP AND manual testing, you could:

1. **Add an HTTP API endpoint** for pushing messages:
   ```python
   async def push_api_handler(request):
       data = await request.json()
       message = data.get('message', '')
       await send_to_all_clients(f"data: {message}\\n\\n")
       return web.json_response({'status': 'success'})
   
   app.router.add_post('/api/push', push_api_handler)
   ```

2. **Then test with curl**:
   ```bash
   curl -X POST http://localhost:8000/api/push \\
        -H "Content-Type: application/json" \\
        -d '{"message":"Test from curl!"}'
   ```

## Expected Workflow

```
User → Cursor AI → MCP Protocol (stdio) → Docker Container
                                              ↓
                                    WebstreamMCP Server
                                              ↓
                                    push_stream tool called
                                              ↓
                                    Web Server (port 8000)
                                              ↓
                                    SSE Stream (/stream)
                                              ↓
                            ┌────────────────┼────────────────┐
                            ↓                ↓                ↓
                      Browser          Node.js Listener   Other Clients
```

## Troubleshooting

### "WebstreamMCP not found in Cursor"

- Make sure you've restarted Cursor
- Check `~/.cursor/mcp.json` is valid JSON
- Look for errors in Cursor's developer console

### "Container not found"

```bash
# Check if container is running
docker ps | grep webstream-mcp-server

# Start if not running
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d
```

### "Port 8000 not accessible"

```bash
# Check container logs
docker-compose logs webstream-mcp-server

# Verify port mapping
docker port webstream-mcp-server
```

### "No messages appearing"

1. Make sure your listener is connected FIRST
2. Then push the message via Cursor
3. Check the container logs for errors

## Demo Commands for Cursor

Try these commands in Cursor's chat:

- `"Push 'Server started successfully' to the webstream"`
- `"Send 'User logged in' to all stream listeners"`
- `"Broadcast 'Build completed' on port 8000"`
- `"Push 'Error: Connection failed' to the webstream"`
- `"Send a test message to the stream"`

## Success Indicators

When everything is working, you should see:

1. **In Cursor**: Confirmation that message was pushed
2. **In Browser** (localhost:8000): Message appears in dashboard
3. **In Node Listener**: Event logged with timestamp
4. **In Docker Logs**: "Active clients" count and message sent

## Need Help?

- Check container logs: `docker-compose logs -f webstream-mcp-server`
- Test connection: `node test-connection.js`
- View dashboard: http://localhost:8000
- Read full docs: `README.md`, `DOCKER_USAGE.md`

