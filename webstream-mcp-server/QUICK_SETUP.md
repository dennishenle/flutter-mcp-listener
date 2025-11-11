# Quick Setup - Claude Desktop + WebstreamMCP

## 🚀 3-Minute Setup

### Step 1: Edit Claude Desktop Config

**File Location** (macOS):
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Add This**:
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

### Step 2: Start Docker Container

```bash
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d
```

### Step 3: Restart Claude Desktop

Quit completely (`Cmd+Q`) and reopen.

### Step 4: Test It!

**In Claude Desktop, type:**
```
Push the message 'Hello from Claude!' to the webstream
```

**Start your listener to see it:**
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

**Or open in browser:**
```
http://localhost:8000
```

## ✅ That's It!

You're now ready to push messages from Claude Desktop to your webstream!

---

## 📖 Full Documentation

- **Complete Setup Guide**: `CLAUDE_DESKTOP_SETUP.md`
- **Docker Usage**: `DOCKER_USAGE.md`
- **Cursor Integration**: `CURSOR_INTEGRATION.md`
- **Implementation Details**: `CLAUDE.md`

## 🔍 Troubleshooting

**Container not running?**
```bash
docker-compose ps
docker-compose up -d
```

**Can't connect?**
```bash
curl http://localhost:8000
```

**Check logs:**
```bash
docker-compose logs -f
```

## 💡 Example Commands for Claude

```
"Push 'Server started' to the webstream"
"Send 'User logged in' to all stream listeners"
"Broadcast 'Build completed' on the stream"
"Push an error message to the webstream"
```

Enjoy! 🎉

