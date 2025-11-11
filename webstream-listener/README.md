# WebStream Listener

A Node.js client that listens to the WebstreamMCP Server-Sent Events (SSE) stream and displays messages in real-time.

## ✅ Status Check

Your listener is **correctly configured** and ready to use! ✨

### What's Working:
- ✅ Correct URL configuration (`http://localhost:8000/stream`)
- ✅ Proper EventSource implementation
- ✅ Error handling and auto-reconnect
- ✅ Event counting and timestamping
- ✅ Graceful shutdown on Ctrl+C
- ✅ Docker container running

## 🚀 Quick Start

### 1. Start the Web Server (First Time Only)

The web server starts on-demand when the first message is pushed. You have two options:

**Option A: Use the helper script**
```bash
./start-webserver.sh
```

**Option B: Ask Claude Desktop**
```
"Push the message 'Server starting!' to the webstream"
```

### 2. Start the Listener

```bash
node stream-listener.js
```

You should see:
```
🌐 WebstreamMCP Client Starting...
📡 Connecting to: http://localhost:8000/stream

✅ Connected to webstream!
⏳ Waiting for messages...
```

### 3. Send Messages

Use Claude Desktop to push messages:
```
"Push 'Hello World' to the webstream"
"Send 'Testing the stream!' to all listeners"
"Broadcast 'This is amazing!' on the stream"
```

## 📁 Files

- **`stream-listener.js`** - Main listener application
- **`test-connection.js`** - Connection test utility
- **`start-webserver.sh`** - Helper script to initialize web server
- **`QUICK_START.md`** - Detailed setup instructions
- **`TEST_GUIDE.md`** - Comprehensive testing guide
- **`package.json`** - Dependencies

## 🧪 Testing

### Test Connection
```bash
node test-connection.js
```

### Test with curl
```bash
curl -N http://localhost:8000/stream
```

### View Web Dashboard
```bash
open http://localhost:8000
```

## 📊 Example Output

When messages are received:

```
📨 Event #1 received at 3:45:30 PM
📝 Data: [2025-11-11T14:45:30.123Z] Hello World
────────────────────────────────────────────────────────

📨 Event #2 received at 3:45:35 PM
📝 Data: [2025-11-11T14:45:35.456Z] Testing the stream!
────────────────────────────────────────────────────────

📨 Event #3 received at 3:45:40 PM
📝 Data: [2025-11-11T14:45:40.789Z] This is amazing!
────────────────────────────────────────────────────────
```

## 🔧 Requirements

- Node.js (installed ✓)
- `eventsource` package (installed ✓)
- WebstreamMCP Docker container running (running ✓)

## 📖 Documentation

- **Quick Start**: See `QUICK_START.md` for step-by-step instructions
- **Testing**: See `TEST_GUIDE.md` for comprehensive testing scenarios
- **Docker Setup**: See `../webstream-mcp-server/DOCKER_USAGE.md`

## 🎯 Use Cases

- Real-time notifications from your LLM
- Event monitoring and logging
- Multi-client message broadcasting
- Integration with other services
- Dashboard updates
- Alert systems

## 🐛 Troubleshooting

### Connection Failed

**Problem**: `❌ Failed to connect to stream`

**Solution**: The web server hasn't started yet. Run:
```bash
./start-webserver.sh
```
or ask Claude to push a message.

### Container Not Running

**Problem**: Docker container not found

**Solution**: Start the container:
```bash
cd ../webstream-mcp-server
docker-compose up -d
```

### Port Already in Use

**Problem**: Port 8000 is occupied

**Solution**: Check what's using it:
```bash
lsof -i :8000
```

## 💡 Tips

1. **Keep it running** - The listener auto-reconnects on disconnect
2. **Multiple instances** - Run multiple listeners simultaneously
3. **Web dashboard** - Open `http://localhost:8000` for visual monitoring
4. **Keepalive** - Connection maintained with 30-second pings
5. **Timestamps** - All messages include UTC timestamps

## 📈 Next Steps

1. Start your listener: `node stream-listener.js`
2. Open the web dashboard: `http://localhost:8000`
3. Ask Claude to push messages
4. Watch them appear in real-time!

## 🎉 You're Ready!

Everything is set up correctly. Your listener will work perfectly once you start pushing messages through Claude Desktop!

For more details, see:
- `QUICK_START.md` - Step-by-step guide
- `TEST_GUIDE.md` - Testing scenarios

