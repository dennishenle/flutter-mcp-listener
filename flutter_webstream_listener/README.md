# Flutter Webhook Listener

A beautiful Flutter app that receives webhook messages from the WebhookMCP Server via HTTP POST requests. No persistent connections required!

## 🔄 What Changed?

This app has been **converted from SSE (Server-Sent Events) to Webhooks**:

- ❌ **Before**: Persistent connection to server stream
- ✅ **Now**: Runs local HTTP server and receives webhook POST requests
- ✅ **Benefit**: No connection management, simpler architecture, works better on mobile

## 🚀 Quick Start

### 1. Ensure Webhook MCP Server is Running

```bash
cd /Users/dennis/projects/flutter-meetup-041225/webstream-mcp-server
docker-compose up -d
```

### 2. Run the Flutter App

```bash
cd /Users/dennis/projects/flutter-meetup-041225/flutter_webstream_listener
flutter pub get
flutter run
```

The app will:
- Start an HTTP server on port 3000
- Automatically register its webhook with the MCP server
- Show "Registered ✓" when ready

### 3. Send Test Messages

Push messages to see them appear in the app:

```bash
curl -X POST http://localhost:8000/api/push \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello from webhooks!"}'
```

Or use Claude/Cursor:
```
"Push 'Testing Flutter webhook app!' to the webhooks"
```

## 📱 Platform-Specific Configuration

### Web & Desktop (macOS, Windows, Linux)
✅ **Works with default settings**

The app automatically uses the correct configuration for desktop platforms.

### iOS Simulator
✅ **Works with default settings**

iOS Simulator can access `localhost` from your Mac.

### Android Emulator
✅ **Automatically configured**

The app automatically detects Android platform and uses `10.0.2.2` for the MCP server URL and webhook registration.

### Physical Devices (iPhone, Android Phone)
⚠️ **Needs your computer's IP address**

Find your computer's IP address:

**On macOS:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**On Windows:**
```cmd
ipconfig
```

Then update `main.dart` around line 50:

```dart
// Change from:
final String _mcpServerUrl = 'http://localhost:8000';

// To (replace with your computer's IP):
final String _mcpServerUrl = 'http://192.168.1.100:8000';

// Also update the _webhookUrl getter to return your computer's IP:
String get _webhookUrl {
  return 'http://192.168.1.100:$_localPort/webhook';
}
```

**Important**: Make sure your device is on the same WiFi network as your computer!

## ✨ Features

### HTTP Server
- Runs embedded HTTP server on port 3000
- Receives webhook POST requests at `/webhook`
- Automatic lifecycle management

### Auto-Registration
- Automatically registers webhook on startup
- Auto-unregisters on app close
- Shows registration status in UI

### Message Display
- Newest messages at the top
- Event counter shows total messages received
- Each message shows its event number
- Clean, Material Design 3 UI

### Controls
- **Refresh button**: Restart server and re-register
- **Clear button**: Clear all messages
- **Status indicator**: Shows registration state with color

### Status Colors
- 🟢 **Green**: Registered and ready
- 🟠 **Orange**: Starting or registering
- 🔴 **Red**: Error state

## 🧪 Testing

### Test 1: Registration
Run the app and check the status bar:
- Should show "Registered ✓ (port 3000)" with green background

Verify registration:
```bash
curl http://localhost:8000/api/webhooks
# Should show your webhook URL in the list
```

### Test 2: Receive Messages
Push a test message:
```bash
curl -X POST http://localhost:8000/api/push \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message 1"}'
```

The message should appear immediately in the app.

### Test 3: Multiple Messages
Push several messages quickly:
```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/push \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"Message $i\"}"
  sleep 1
done
```

All 5 messages should appear in order (newest at top).

### Test 4: Direct Webhook Test
Test the webhook endpoint directly:
```bash
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":"Direct test","timestamp":"2025-11-25T12:00:00Z"}'
```

The message should appear in the app.

## 🎨 UI Components

### Status Bar
Shows:
- Registration status with icon
- Event count (when registered)
- Local port number

### Message List
Each message card shows:
- Event number badge
- Message content with timestamp
- "Event #X" subtitle

### Empty State
When no messages received:
- Message icon
- "No messages yet" text
- Helpful description

## 🔧 How It Works

### Webhook Architecture
The app uses webhooks instead of persistent connections:
- Runs a local HTTP server (Shelf package)
- Registers webhook URL with MCP server
- MCP server makes HTTP POST when messages arrive
- App parses JSON payload and displays message

### Data Flow
```
User (Claude/Cursor)
    ↓
    "Push message to webhooks"
    ↓
MCP Server (port 8000)
    ↓
    HTTP POST to registered webhooks
    ↓
Flutter HTTP Server (port 3000)
    ↓
    POST /webhook endpoint
    ↓
JSON Parser
    ↓
UI Update (setState)
    ↓
Message List Display
```

### Webhook Payload Format
Messages come as JSON:
```json
{
  "message": "Your message here",
  "timestamp": "2025-11-25T12:34:56.789012+00:00"
}
```

The app:
- Receives POST request at `/webhook`
- Parses JSON body
- Extracts message and timestamp
- Updates UI with new message
- Responds with 200 OK

## 🐛 Troubleshooting

### "Registration failed"

**Problem**: Can't register with MCP server.

**Solutions**:

1. Check MCP server is running:
   ```bash
   docker ps | grep webhook-mcp-server
   ```

2. Test server accessibility:
   ```bash
   curl http://localhost:8000/api/webhooks
   ```

3. For mobile devices, use correct IP address (see Platform-Specific Configuration above)

4. Check server logs:
   ```bash
   docker-compose logs -f webstream-mcp-server
   ```

### "Error starting server: Address already in use"

**Problem**: Port 3000 is already in use.

**Solutions**:

1. Find what's using port 3000:
   ```bash
   lsof -i :3000    # macOS/Linux
   netstat -ano | findstr :3000    # Windows
   ```

2. Kill the process or change the port in `main.dart`:
   ```dart
   final int _localPort = 3001;  // Use different port
   ```

### Messages Not Appearing

**Problem**: Registered but no messages show up.

**Solutions**:

1. Verify webhook is registered:
   ```bash
   curl http://localhost:8000/api/webhooks
   ```

2. Test webhook directly:
   ```bash
   curl -X POST http://localhost:3000/webhook \
     -H "Content-Type: application/json" \
     -d '{"message":"Test","timestamp":"2025-01-01T00:00:00Z"}'
   ```

3. Push via MCP server:
   ```bash
   curl -X POST http://localhost:8000/api/push \
     -H "Content-Type: application/json" \
     -d '{"message":"Test"}'
   ```

4. Check Flutter debug console for errors

### Can't Connect from Phone

**Problem**: Physical device can't reach localhost.

**Solutions**:

1. Make sure phone and computer are on same WiFi

2. Find your computer's IP:
   ```bash
   ifconfig | grep "inet "    # macOS/Linux
   ipconfig                   # Windows
   ```

3. Update both URLs in `main.dart`:
   - `_mcpServerUrl`: Where the MCP server is
   - `_webhookUrl`: Where the Flutter app is (your computer's IP + port 3000)

4. Make sure firewall allows ports 8000 and 3000

## 📊 Architecture

```
Flutter App
    ├─ Shelf HTTP Server (port 3000)
    │   └─ POST /webhook endpoint
    ├─ HTTP Client (registration)
    └─ State Management (setState)
        ↓
    UI Components
        ├─ Status Bar (registration info)
        ├─ Message List (ListView)
        └─ Controls (refresh, clear)
```

## 🎯 Use Cases

- **Development Notifications**: Receive build status, test results
- **CI/CD Updates**: Get notified of deployment status
- **System Monitoring**: Receive alerts and warnings
- **Chat Messages**: Display real-time messages
- **IoT Events**: Monitor device status and sensor data
- **Any Push Notifications**: General-purpose webhook receiver

## 📚 Code Structure

### State Variables
- `_messages`: List of received messages
- `_connectionStatus`: Current registration state
- `_server`: HTTP server instance
- `_eventCount`: Total messages received

### Key Methods
- `_startWebhookServer()`: Starts HTTP server and registers webhook
- `_handleWebhookRequest()`: Processes incoming webhook POST requests
- `_registerWebhook()`: Registers with MCP server
- `_unregisterWebhook()`: Unregisters on app close
- `_reconnect()`: Restart server and re-register

### UI Sections
- AppBar with controls
- Status bar with registration info
- Message list or empty state

## 🚀 Advantages of Webhooks

### vs Server-Sent Events (SSE)

| Feature | Webhooks | SSE |
|---------|----------|-----|
| **Connection** | No persistent connection | Persistent connection required |
| **Mobile Battery** | Better (no keep-alive) | Drains battery faster |
| **Reliability** | More reliable on mobile | Can disconnect frequently |
| **Scalability** | Scales better | Holds connections open |
| **Complexity** | Simpler architecture | More complex state management |
| **Firewall** | Works better behind NAT | Connection issues common |

## 📖 Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0   # For webhook registration
  shelf: ^1.4.0  # HTTP server framework
```

## ✅ Testing Checklist

- [ ] App starts successfully
- [ ] HTTP server starts on port 3000
- [ ] Status shows "Registered ✓"
- [ ] Webhook appears in server's list
- [ ] Messages arrive when pushed
- [ ] Event count increments
- [ ] Direct webhook test works
- [ ] Refresh button re-registers
- [ ] Clear button works
- [ ] UI looks good on your platform

## 🎉 You're All Set!

Your Flutter app is now ready to receive webhook messages from the MCP server!

Enjoy your webhook-powered notifications! 📱✨

## 🔗 Related Documentation

- Main MCP Server: `../webstream-mcp-server/readme.md`
- MCP Server API: `http://localhost:8000` (web dashboard)
- Webhook Management: `http://localhost:8000/api/webhooks`
