# Flutter WebStream Listener

A beautiful Flutter app for listening to the WebstreamMCP Server-Sent Events (SSE) stream in real-time.

## ✅ Fixed Issues

The app now correctly:
- ✅ Connects to the `/stream` endpoint (was missing before)
- ✅ Parses SSE format with `data:` prefix
- ✅ Auto-reconnects on disconnect or error
- ✅ Shows event count and connection status
- ✅ Displays messages newest-first
- ✅ Handles keepalive pings properly

## 🚀 Quick Start

### 1. Ensure WebStream Server is Running

```bash
cd /Users/dennis/projects/MCP/webstream-mcp-server
docker-compose up -d
```

### 2. Run the Flutter App

```bash
cd /Users/dennis/projects/MCP/flutter_webstream_listener
flutter run
```

### 3. Send Test Messages

Push messages to see them appear in the app:

```bash
curl -X POST http://localhost:8000/api/push \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello from Flutter!"}'
```

Or use Claude/Cursor:
```
"Push 'Testing Flutter app!' to the webstream"
```

## 📱 Platform-Specific Configuration

### Web & Desktop (macOS, Windows, Linux)
✅ **Works with default settings**

The app uses `http://localhost:8000/stream` which works perfectly on:
- Chrome, Safari, Firefox (Flutter Web)
- macOS app
- Windows app
- Linux app

### iOS Simulator
✅ **Works with default settings**

iOS Simulator can access `localhost` from your Mac.

### Android Emulator
⚠️ **Needs IP address change**

Android emulator uses a special IP for the host machine. Change line 44 in `main.dart`:

```dart
// Change from:
final String _streamUrl = 'http://localhost:8000/stream';

// To:
final String _streamUrl = 'http://10.0.2.2:8000/stream';
```

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

Then update line 44 in `main.dart`:

```dart
// Replace with your computer's IP:
final String _streamUrl = 'http://192.168.1.100:8000/stream';
```

**Important**: Make sure your device is on the same WiFi network as your computer!

## ✨ Features

### Auto-Reconnection
- Automatically reconnects if connection is lost
- 3-second delay after disconnect
- 5-second delay after error

### Message Display
- Newest messages at the top
- Event counter shows total events received
- Each message shows its event number
- Clean, Material Design 3 UI

### Controls
- **Refresh button**: Reconnect to stream
- **Clear button**: Clear all messages
- **Status indicator**: Shows connection state with color

### Status Colors
- 🟢 **Green**: Connected and receiving
- 🟠 **Orange**: Connecting or reconnecting
- 🔴 **Red**: Error state

## 🧪 Testing

### Test 1: Connection
Run the app and check the status bar:
- Should show "Connected ✓" with green background

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

### Test 4: Auto-Reconnect
1. Stop the Docker container:
   ```bash
   docker-compose down
   ```
2. App should show "Disconnected" or error
3. Restart container:
   ```bash
   docker-compose up -d
   ```
4. App should automatically reconnect within 3-5 seconds

## 🎨 UI Components

### Status Bar
Shows:
- Connection status with icon
- Event count (when connected)
- Stream URL

### Message List
Each message card shows:
- Event number badge
- Message content
- "Event #X" subtitle

### Empty State
When no messages received:
- Message icon
- "No messages yet" text
- Helpful description

## 🔧 How It Works

### SSE (Server-Sent Events)
The app uses SSE protocol which:
- Keeps connection open
- Server pushes data when available
- Automatic reconnection support
- Text-based, simple format

### Data Flow
```
WebStream Server (port 8000)
    ↓
    /stream endpoint (SSE)
    ↓
Flutter HTTP Client
    ↓
UTF-8 Decoder
    ↓
Line Parser (data: prefix)
    ↓
UI Update (setState)
    ↓
Message List Display
```

### SSE Format
Messages come as:
```
data: [2025-11-11T08:03:02...] Your message here

: keepalive

data: [2025-11-11T08:03:05...] Another message

```

The app:
- Parses lines starting with `data:`
- Extracts message after the prefix
- Ignores keepalive lines (starting with `:`)
- Updates UI with new messages

## 🐛 Troubleshooting

### "Error: Connection refused"

**Problem**: Can't connect to the server.

**Solutions**:

1. Check server is running:
   ```bash
   docker ps | grep webstream-mcp-server
   ```

2. Test server accessibility:
   ```bash
   curl http://localhost:8000/stream
   ```

3. For mobile devices, use correct IP address (see Platform-Specific Configuration above)

### "Error: HTTP 404"

**Problem**: Wrong URL.

**Solution**: Ensure you're using `/stream` endpoint:
```dart
final String _streamUrl = 'http://localhost:8000/stream';
//                                                  ^^^^^^^ Important!
```

### Messages Not Appearing

**Problem**: Connected but no messages show up.

**Solutions**:

1. Push a test message:
   ```bash
   curl -X POST http://localhost:8000/api/push \
     -H "Content-Type: application/json" \
     -d '{"message":"Test"}'
   ```

2. Check app is parsing correctly (should see event count increase)

3. Try clearing messages with the clear button

### Can't Connect from Phone

**Problem**: Physical device can't reach localhost.

**Solutions**:

1. Make sure phone and computer are on same WiFi

2. Find your computer's IP:
   ```bash
   ifconfig | grep "inet "
   ```

3. Update the URL in `main.dart` with your IP

4. Make sure firewall allows port 8000

## 📊 Architecture

```
Flutter App
    ├─ HTTP Client (http package)
    ├─ Stream Subscription
    ├─ UTF-8 Decoder
    └─ SSE Parser
        ↓
    State Management (setState)
        ↓
    UI Components
        ├─ Status Bar (connection info)
        ├─ Message List (ListView)
        └─ Controls (refresh, clear)
```

## 🎯 Use Cases

- **Development Monitoring**: Watch real-time events during development
- **Build Notifications**: See build status messages from CI/CD
- **System Alerts**: Monitor system events and errors
- **Chat/Messaging**: Display real-time messages
- **IoT Dashboard**: Show sensor data or device status
- **Live Updates**: Any real-time notification system

## 📚 Code Structure

### State Variables
- `_messages`: List of received messages
- `_connectionStatus`: Current connection state
- `_streamSubscription`: Active stream subscription
- `_eventCount`: Total events received

### Key Methods
- `_connectToStream()`: Establishes SSE connection
- `_reconnect()`: Manual reconnect trigger
- `_clearMessages()`: Clear message history

### UI Sections
- AppBar with controls
- Status bar with connection info
- Message list or empty state

## 🚀 Next Steps

### Enhancements You Could Add:

1. **Message Filtering**
   - Filter by keyword
   - Show only errors/warnings

2. **Message Persistence**
   - Save messages to local storage
   - Load history on startup

3. **Export Functionality**
   - Export messages as JSON
   - Share messages

4. **Themes**
   - Dark mode
   - Custom color schemes

5. **Notifications**
   - Local notifications for new messages
   - Sound alerts

6. **Multiple Streams**
   - Connect to multiple servers
   - Switch between streams

## 📖 Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0  # For SSE connection
```

## ✅ Testing Checklist

- [ ] App connects successfully
- [ ] Status shows "Connected ✓"
- [ ] Messages appear when pushed
- [ ] Event count increments
- [ ] Auto-reconnect works
- [ ] Clear button works
- [ ] Refresh button works
- [ ] UI looks good on your platform

## 🎉 You're All Set!

Your Flutter app is now ready to receive real-time messages from the WebstreamMCP server!

Enjoy your live event stream! 📱✨
