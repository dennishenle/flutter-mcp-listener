# Claude Desktop Setup Guide for WebstreamMCP

## Quick Setup

### 1. Locate Claude Desktop Configuration File

On macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

On Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

On Linux:
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Add WebstreamMCP Configuration

Open the configuration file and add the WebstreamMCP server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "webstream": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "webstream-mcp-server",
        "python",
        "/app/webstream_server.py"
      ]
    }
  }
}
```

**If you already have other MCP servers configured**, add it to the existing list:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "webstream": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "webstream-mcp-server",
        "python",
        "/app/webstream_server.py"
      ]
    }
  }
}
```

### 3. Ensure Docker Container is Running

Before starting Claude Desktop, make sure your webstream container is running:

```bash
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d
```

Verify it's running:
```bash
docker ps | grep webstream-mcp-server
```

### 4. Restart Claude Desktop

1. **Completely quit Claude Desktop** (not just close the window)
   - On macOS: `Cmd+Q` or right-click the app in Dock → Quit
   - On Windows: Exit from system tray
   - On Linux: Close all Claude Desktop processes

2. **Reopen Claude Desktop**

3. **Wait a few seconds** for MCP servers to initialize

### 5. Verify the Connection

In Claude Desktop, you should now see that the MCP server is connected. You can verify by:

1. Looking for the MCP indicator in Claude Desktop's interface
2. Asking Claude: "What MCP tools do you have available?"
3. Claude should mention the `push_stream` tool

## Usage Examples

Once configured, you can ask Claude to push messages to the webstream:

### Basic Message Push

```
"Push the message 'Hello from Claude!' to the webstream"
```

### With Custom Details

```
"Send 'Server started successfully' to all stream listeners"
```

```
"Broadcast 'Build completed at 3:45 PM' on the stream"
```

### System Notifications

```
"Push 'ERROR: Database connection failed' to the webstream"
```

```
"Send 'User john.doe logged in' to all listeners"
```

### Testing

```
"Push a test message to the webstream to verify it's working"
```

## Viewing the Messages

### Option 1: Node.js Listener

Start your listener:
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

You'll see messages appear in real-time:
```
📨 Event #1 received at 3:45:30 PM
📝 Data: [2025-11-11T14:45:30...] Hello from Claude!
```

### Option 2: Web Dashboard

Open in your browser:
```
http://localhost:8000
```

You'll see a live dashboard showing all events as they arrive.

### Option 3: Direct Stream Connection

```bash
curl -N http://localhost:8000/stream
```

## Complete Configuration Example

Here's a complete `claude_desktop_config.json` example:

```json
{
  "mcpServers": {
    "webstream": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "webstream-mcp-server",
        "python",
        "/app/webstream_server.py"
      ]
    }
  },
  "globalShortcut": "CommandOrControl+Shift+Space"
}
```

## Troubleshooting

### "Container not found" Error

**Problem**: Claude Desktop can't find the Docker container.

**Solution**:
```bash
# Check if container is running
docker ps | grep webstream-mcp-server

# If not running, start it
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d

# Verify it's healthy
docker-compose ps
```

### MCP Server Not Appearing in Claude

**Problem**: WebstreamMCP doesn't show up in Claude Desktop.

**Solutions**:

1. **Check configuration file syntax**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```
   If this errors, your JSON is invalid.

2. **Verify file location** - Make sure you edited the correct file.

3. **Restart Claude Desktop completely** - Must quit and reopen, not just close window.

4. **Check Claude Desktop logs**:
   - On macOS: `~/Library/Logs/Claude/`
   - Look for MCP initialization errors

### "Tool not available" Error

**Problem**: Claude says the `push_stream` tool isn't available.

**Solutions**:

1. **Restart Claude Desktop** after config changes.

2. **Check container logs**:
   ```bash
   docker-compose logs webstream-mcp-server
   ```

3. **Test container manually**:
   ```bash
   echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | \
     docker exec -i webstream-mcp-server python /app/webstream_server.py
   ```

### Messages Not Appearing in Listener

**Problem**: Claude says message was pushed but listener doesn't receive it.

**Solutions**:

1. **Check listener is running**:
   ```bash
   ps aux | grep "node stream-listener"
   ```

2. **Restart listener**:
   ```bash
   cd /Users/dennis/projects/MCP/webstream-listener
   node stream-listener.js
   ```

3. **Check web server is accessible**:
   ```bash
   curl http://localhost:8000
   ```

4. **View container logs**:
   ```bash
   docker-compose logs -f webstream-mcp-server
   ```

### Permission Denied Error

**Problem**: Docker permission errors.

**Solution**:
```bash
# Ensure your user can run docker commands
docker ps

# If permission denied, you may need to add your user to docker group
# or use Docker Desktop on macOS/Windows
```

## Testing the Full Pipeline

Follow these steps to verify everything works:

### Step 1: Start the Container
```bash
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d
```

### Step 2: Start the Listener
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

You should see:
```
✅ Connected to webstream!
⏳ Waiting for messages...
```

### Step 3: Open Web Dashboard
Open http://localhost:8000 in your browser.

### Step 4: Ask Claude
In Claude Desktop:
```
"Push the message 'Testing the full pipeline!' to the webstream"
```

### Step 5: Verify
The message should appear in:
- ✅ Your terminal (Node.js listener)
- ✅ Your browser (web dashboard)
- ✅ Container logs

## Alternative: Using HTTP API

If you want to test without Claude Desktop, you can also push messages via HTTP:

```bash
curl -X POST http://localhost:8000/api/push \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message via API"}'
```

Response:
```json
{
  "status": "success",
  "message": "Test message via API",
  "timestamp": "2025-11-11T...",
  "clients": 1
}
```

## Architecture Overview

```
Claude Desktop
    ↓
    ↓ MCP Protocol (stdio via docker exec)
    ↓
Docker Container (webstream-mcp-server)
    ├─ MCP Server (stdio)
    └─ Web Server (port 8000)
        ↓
        ├─ / (Web Dashboard)
        ├─ /stream (SSE Stream)
        └─ /api/push (HTTP API)
            ↓
            ↓ Server-Sent Events
            ↓
    ┌───────┴────────┐
    ↓                ↓
Node.js Listener  Browser
```

## Advanced Configuration

### Custom Port

If you need to use a different port, update `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Host port 9000 → Container port 8000
```

Then push with custom port:
```
"Push 'test message' to the webstream on port 9000"
```

### Environment Variables

You can add environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=DEBUG
```

## Security Considerations

### Development vs Production

This setup is designed for **local development**:

- ✅ Perfect for local AI assistant integration
- ✅ Great for development and testing
- ⚠️ **Not recommended for production** without:
  - Authentication
  - HTTPS/TLS
  - Rate limiting
  - Input validation
  - Network isolation

### Network Access

By default, the server binds to `0.0.0.0:8000`, making it accessible:
- ✅ From localhost
- ✅ From Docker containers
- ⚠️ From your local network (if firewall allows)

For strict localhost-only access, modify `docker-compose.yml`:
```yaml
ports:
  - "127.0.0.1:8000:8000"
```

## Support

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Test the stream**: `curl -N http://localhost:8000/stream`
3. **Verify configuration**: Check your JSON syntax
4. **Restart everything**: Container, listener, and Claude Desktop

## Next Steps

Once configured, try these workflows:

1. **Build notifications**: "When my code compiles, push 'Build completed' to the stream"
2. **Error alerts**: "Push error messages to the webstream when issues occur"
3. **Status updates**: "Send status updates about task progress to the stream"
4. **Integration**: Connect your own applications to the stream endpoint

Happy streaming! 🚀

