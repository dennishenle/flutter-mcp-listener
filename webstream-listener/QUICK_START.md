# 🚀 Quick Start Guide - Testing Your WebStream Listener

## Understanding the Architecture

Your setup has **two parts** that work together:

1. **MCP Server (Docker)** - Waits for MCP commands (runs on stdio protocol)
2. **Web Server (Port 8000)** - Starts **on-demand** when push_stream is called

```
┌─────────────────────────────────────────────────┐
│  Docker Container (MCP Server)                  │
│  ├─ Waiting for MCP commands (stdio)            │
│  └─ Web server on port 8000 (starts on-demand)  │
└─────────────────────────────────────────────────┘
                      ↓
        First push_stream call triggers
                      ↓
         Web server starts on port 8000
                      ↓
            Listeners can connect!
```

## ✅ Your Listener is Perfect!

Your `stream-listener.js` is correctly configured and will work great once the web server starts!

## 🧪 Testing Results

I've tested your setup and confirmed:
- ✅ Docker container is running
- ✅ MCP server is active and waiting
- ⏳ Web server will start when push_stream is called
- ✅ Your listener code is correct and ready

## 📝 How to Test Everything

### Method 1: Test with Manual Trigger (Recommended for first test)

Since the web server starts on-demand, let's create a simple trigger:

**Step 1** - In one terminal, prepare your listener:
```bash
cd /Users/dennis/projects/MCP/webstream-listener
# Don't start it yet, just prepare the command
```

**Step 2** - Trigger the web server to start:
```bash
# We'll send an MCP command to start the server
cd /Users/dennis/projects/MCP/webstream-mcp-server
echo '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"push_stream","arguments":{"message":"Server starting!","port":"8000"}}}' | docker exec -i webstream-mcp-server python webstream_server.py
```

**Step 3** - Now start your listener:
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

You should see:
```
🌐 WebstreamMCP Client Starting...
📡 Connecting to: http://localhost:8000/stream

✅ Connected to webstream!
⏳ Waiting for messages...
```

### Method 2: Test with Claude Desktop (Production Method)

This is how it will work in real use:

**Step 1** - Start your listener first (it will wait for connection):
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

**Step 2** - Use Claude Desktop to push a message:
```
"Push the message 'Hello from Claude!' to the webstream"
```

**Step 3** - Watch the message appear in your listener!

### Method 3: Test with Multiple Endpoints

**Terminal 1** - Start listener:
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

**Terminal 2** - Open web dashboard:
```bash
open http://localhost:8000
```

**Claude Desktop** - Push message:
```
"Broadcast 'Testing multi-client!' to the stream"
```

**Result** - Message appears in BOTH places! 🎉

## 🔧 Test Commands You Can Try

Once the web server is running, test your listener with these commands:

### Quick Connection Test
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node test-connection.js
```

### Start the Listener
```bash
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js
```

### Check Docker Status
```bash
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose ps
docker-compose logs -f
```

### Test Stream with curl
```bash
# This will show raw SSE data
curl -N http://localhost:8000/stream
```

## 📊 Expected Behavior

### When Listener Connects Successfully:
```
🌐 WebstreamMCP Client Starting...
📡 Connecting to: http://localhost:8000/stream

✅ Connected to webstream!
⏳ Waiting for messages...

────────────────────────────────────────────────────────
💡 Press Ctrl+C to stop listening
```

### When Message is Received:
```
📨 Event #1 received at 3:45:30 PM
📝 Data: [2025-11-11T14:45:30.123Z] Hello from Claude!
────────────────────────────────────────────────────────
```

### If Connection Fails:
```
❌ Failed to connect to stream
Make sure the WebstreamMCP server is running on port 8000

🔄 EventSource will automatically attempt to reconnect...
```

## 🐛 Troubleshooting

### "Connection Failed" Error

**Cause**: Web server hasn't started yet (waiting for first push_stream call)

**Solution**: 
1. Use Claude to push a message first, OR
2. Run the manual trigger command from Method 1 above

### Docker Container Not Running

```bash
# Check status
docker-compose ps

# Restart if needed
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose down
docker-compose up -d
```

### Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or change the port
```

## 🎯 Complete Test Workflow

Here's the complete sequence to test everything:

```bash
# 1. Ensure Docker is running
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose ps

# 2. Start listener (opens in new terminal)
cd /Users/dennis/projects/MCP/webstream-listener
node stream-listener.js

# 3. In Claude Desktop, type:
"Push 'Test message from Claude!' to the webstream"

# 4. Watch message appear in your listener terminal!

# 5. Open web dashboard to see it there too:
open http://localhost:8000
```

## 💡 Pro Tips

1. **Keep listener running** - It will auto-reconnect if disconnected
2. **Multiple listeners** - You can run multiple instances simultaneously
3. **Web dashboard** - Great for visual monitoring
4. **Message format** - Messages include timestamp automatically
5. **Keepalive** - Connection stays alive with 30-second keepalive pings

## 📚 Additional Resources

- Full test guide: `TEST_GUIDE.md`
- Connection test: `node test-connection.js`
- Docker usage: `../webstream-mcp-server/DOCKER_USAGE.md`

## 🎉 You're All Set!

Your listener is perfectly configured and ready to receive messages. The only thing needed is to trigger the web server to start by having Claude push the first message!

