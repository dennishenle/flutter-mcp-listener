#!/bin/bash
# Helper script to trigger the web server to start
# This sends an MCP command to initialize the web server on port 8000

echo "🚀 Starting WebstreamMCP web server..."
echo ""

# Check if Docker container is running
if ! docker ps | grep -q webstream-mcp-server; then
    echo "❌ Error: Docker container 'webstream-mcp-server' is not running"
    echo ""
    echo "Please start it first:"
    echo "  cd /Users/dennis/projects/MCP/webstream-mcp-server"
    echo "  docker-compose up -d"
    exit 1
fi

echo "📡 Sending initialization command to MCP server..."

# Send MCP command to trigger web server startup
# This calls the push_stream tool which starts the web server
RESPONSE=$(echo '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"push_stream","arguments":{"message":"Web server initialized","port":"8000","host":"0.0.0.0"}}}' | docker exec -i webstream-mcp-server python /app/webstream_server.py 2>&1)

echo ""
echo "📋 Response from server:"
echo "$RESPONSE"
echo ""

# Wait a moment for server to start
sleep 2

# Test if server is accessible
echo "🧪 Testing connection to http://localhost:8000..."
if curl -s -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Web server is running and accessible!"
    echo ""
    echo "🎉 Success! You can now:"
    echo "   1. Start your listener: node stream-listener.js"
    echo "   2. Open web dashboard: http://localhost:8000"
    echo "   3. Connect with curl: curl -N http://localhost:8000/stream"
    echo ""
else
    echo "⚠️  Could not connect to web server yet"
    echo ""
    echo "💡 The server might need a moment to start, or it may require"
    echo "   an actual client connection to fully initialize."
    echo ""
    echo "Try running your listener now:"
    echo "   node stream-listener.js"
    echo ""
fi

