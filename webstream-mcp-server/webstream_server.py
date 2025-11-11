#!/usr/bin/env python3
"""
Simple WebstreamMCP Server - Provides a web server with SSE streaming capability
"""
import os
import sys
import logging
import asyncio
import threading
from datetime import datetime, timezone
from aiohttp import web
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("webstream-server")

# Initialize MCP server
mcp = FastMCP("webstream")

# Configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"

# Global storage for the web server and stream clients
web_app = None
web_runner = None
stream_clients = set()

# === UTILITY FUNCTIONS ===

async def send_to_all_clients(message: str):
    """Send a message to all connected SSE clients."""
    disconnected = set()
    for client in stream_clients:
        try:
            await client.write(message.encode())
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            disconnected.add(client)
    
    # Remove disconnected clients
    stream_clients.difference_update(disconnected)
    logger.info(f"Active clients: {len(stream_clients)}")

async def stream_handler(request):
    """Handle SSE stream connections."""
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    await response.prepare(request)
    
    # Add client to the set
    stream_clients.add(response)
    logger.info(f"New client connected. Total clients: {len(stream_clients)}")
    
    try:
        # Send initial connection message
        await response.write(f"data: Connected at {datetime.now(timezone.utc).isoformat()}\n\n".encode())
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)  # Send keepalive every 30 seconds
            await response.write(b": keepalive\n\n")
    except Exception as e:
        logger.info(f"Client disconnected: {e}")
    finally:
        stream_clients.discard(response)
        logger.info(f"Client removed. Total clients: {len(stream_clients)}")
    
    return response

async def index_handler(request):
    """Serve a simple HTML page for testing."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebstreamMCP - Event Stream</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            #events { background: #f9f9f9; padding: 15px; border-radius: 4px; min-height: 200px; max-height: 400px; overflow-y: auto; border: 1px solid #ddd; }
            .event { margin: 5px 0; padding: 8px; background: white; border-left: 3px solid #4CAF50; }
            .timestamp { color: #666; font-size: 0.9em; }
            .status { margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 WebstreamMCP Event Stream</h1>
            <div class="status">
                <strong>Status:</strong> <span id="status">Connecting...</span><br>
                <strong>Events Received:</strong> <span id="count">0</span>
            </div>
            <h2>Live Events</h2>
            <div id="events"></div>
        </div>
        <script>
            const eventSource = new EventSource('/stream');
            const eventsDiv = document.getElementById('events');
            const statusSpan = document.getElementById('status');
            const countSpan = document.getElementById('count');
            let eventCount = 0;
            
            eventSource.onopen = () => {
                statusSpan.textContent = 'Connected ✅';
                statusSpan.style.color = 'green';
            };
            
            eventSource.onmessage = (event) => {
                eventCount++;
                countSpan.textContent = eventCount;
                
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event';
                const timestamp = new Date().toLocaleTimeString();
                eventDiv.innerHTML = `<span class="timestamp">${timestamp}</span><br>${event.data}`;
                eventsDiv.insertBefore(eventDiv, eventsDiv.firstChild);
            };
            
            eventSource.onerror = () => {
                statusSpan.textContent = 'Disconnected ❌';
                statusSpan.style.color = 'red';
            };
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def api_push_handler(request):
    """API endpoint to push messages to the stream (for testing and external use)."""
    try:
        data = await request.json()
        message = data.get('message', '')
        
        if not message:
            return web.json_response({'error': 'Message is required'}, status=400)
        
        # Format the message with timestamp
        timestamp = datetime.now(timezone.utc).isoformat()
        formatted_message = f"data: [{timestamp}] {message}\n\n"
        
        # Send to all clients
        await send_to_all_clients(formatted_message)
        
        client_count = len(stream_clients)
        logger.info(f"API push: '{message}' sent to {client_count} clients")
        
        return web.json_response({
            'status': 'success',
            'message': message,
            'timestamp': timestamp,
            'clients': client_count
        })
    except Exception as e:
        logger.error(f"Error in api_push_handler: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def setup_web_server(port: int, host: str):
    """Set up and start the web server."""
    global web_app, web_runner
    
    if web_runner:
        logger.info("Web server already running")
        return True
    
    try:
        web_app = web.Application()
        web_app.router.add_get('/', index_handler)
        web_app.router.add_get('/stream', stream_handler)
        web_app.router.add_post('/api/push', api_push_handler)
        
        web_runner = web.AppRunner(web_app)
        await web_runner.setup()
        
        site = web.TCPSite(web_runner, host, port)
        await site.start()
        
        logger.info(f"Web server started on http://{host}:{port}")
        return True
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        return False

# === MCP TOOLS ===

@mcp.tool()
async def push_stream(message: str = "", port: str = "8000", host: str = "0.0.0.0") -> str:
    """Push a message to all connected webstream clients via Server-Sent Events."""
    logger.info(f"Executing push_stream with message: {message}")
    
    if not message.strip():
        return "❌ Error: Message is required"
    
    try:
        # Parse port
        port_int = int(port) if port.strip() else DEFAULT_PORT
        host_str = host.strip() if host.strip() else DEFAULT_HOST
        
        # Ensure web server is running
        await setup_web_server(port_int, host_str)
        
        # Format the message with timestamp
        timestamp = datetime.now(timezone.utc).isoformat()
        formatted_message = f"data: [{timestamp}] {message}\n\n"
        
        # Send to all clients
        await send_to_all_clients(formatted_message)
        
        client_count = len(stream_clients)
        
        return f"""✅ Message pushed successfully!

📊 Details:
- Message: {message}
- Timestamp: {timestamp}
- Active clients: {client_count}
- Server: http://{host_str}:{port_int}

💡 To view the stream, open http://{host_str}:{port_int} in a browser or connect via EventSource."""
        
    except ValueError:
        return f"❌ Error: Invalid port number: {port}"
    except Exception as e:
        logger.error(f"Error in push_stream: {e}")
        return f"❌ Error: {str(e)}"

# === SERVER STARTUP ===
def run_webserver_in_thread():
    """Run the web server in a separate thread with its own event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def start_server():
        logger.info("Initializing web server on port 8000...")
        success = await setup_web_server(DEFAULT_PORT, DEFAULT_HOST)
        
        if success:
            logger.info(f"✓ Web server ready at http://{DEFAULT_HOST}:{DEFAULT_PORT}")
            logger.info(f"✓ Stream endpoint: http://{DEFAULT_HOST}:{DEFAULT_PORT}/stream")
            logger.info(f"✓ Dashboard available at http://{DEFAULT_HOST}:{DEFAULT_PORT}")
        else:
            logger.error("Failed to start web server")
            return
        
        # Keep the event loop running forever
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except asyncio.CancelledError:
            logger.info("Web server shutting down...")
    
    try:
        loop.run_until_complete(start_server())
    finally:
        loop.close()

if __name__ == "__main__":
    logger.info("Starting WebstreamMCP server...")
    
    try:
        # Start web server in a background thread
        # This ensures it has its own event loop that stays active
        webserver_thread = threading.Thread(target=run_webserver_in_thread, daemon=True)
        webserver_thread.start()
        
        # Give the web server a moment to start
        import time
        time.sleep(1)
        
        # Start MCP server (blocking call)
        logger.info("MCP server ready for commands")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)