#!/usr/bin/env python3
"""
Simple WebhookMCP Server - Provides a web server with webhook delivery capability
"""
import os
import sys
import logging
import asyncio
import threading
from datetime import datetime, timezone
from aiohttp import web, ClientSession
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("webhook-server")

# Initialize MCP server
mcp = FastMCP("webhook")

# Configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"

# Global storage for the web server and registered webhooks
web_app = None
web_runner = None
registered_webhooks = set()  # Set of registered webhook URLs
client_session = None  # HTTP client session for making webhook calls

# === UTILITY FUNCTIONS ===

async def get_client_session():
    """Get or create HTTP client session."""
    global client_session
    if client_session is None or client_session.closed:
        client_session = ClientSession()
    return client_session

async def send_to_all_webhooks(message: str):
    """Send a message to all registered webhooks via HTTP POST."""
    if not registered_webhooks:
        logger.warning("No webhooks registered")
        return 0
    
    session = await get_client_session()
    failed_webhooks = set()
    success_count = 0
    
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "message": message,
        "timestamp": timestamp
    }
    
    # Send to all webhooks in parallel
    tasks = []
    for webhook_url in registered_webhooks:
        tasks.append(send_webhook(session, webhook_url, payload))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for webhook_url, result in zip(list(registered_webhooks), results):
        if isinstance(result, Exception):
            logger.error(f"Failed to send to webhook {webhook_url}: {result}")
            failed_webhooks.add(webhook_url)
        elif result:
            success_count += 1
            logger.info(f"Successfully sent to webhook: {webhook_url}")
        else:
            logger.error(f"Failed to send to webhook: {webhook_url}")
            failed_webhooks.add(webhook_url)
    
    # Remove failed webhooks after multiple failures (optional)
    # For now, we keep them all
    
    logger.info(f"Sent to {success_count}/{len(registered_webhooks)} webhooks")
    return success_count

async def send_webhook(session, webhook_url: str, payload: dict):
    """Send a single webhook request."""
    try:
        async with session.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        ) as response:
            if response.status == 200:
                return True
            else:
                logger.warning(f"Webhook {webhook_url} returned status {response.status}")
                return False
    except Exception as e:
        logger.error(f"Error sending webhook to {webhook_url}: {e}")
        return False

async def register_webhook_handler(request):
    """Register a webhook URL to receive push notifications."""
    try:
        data = await request.json()
        webhook_url = data.get('webhook_url', '')
        
        if not webhook_url:
            return web.json_response({'error': 'webhook_url is required'}, status=400)
        
        # Validate URL format
        if not webhook_url.startswith(('http://', 'https://')):
            return web.json_response({'error': 'Invalid webhook URL format'}, status=400)
        
        registered_webhooks.add(webhook_url)
        logger.info(f"Registered webhook: {webhook_url}")
        
        return web.json_response({
            'status': 'success',
            'webhook_url': webhook_url,
            'total_webhooks': len(registered_webhooks)
        })
    except Exception as e:
        logger.error(f"Error in register_webhook_handler: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def unregister_webhook_handler(request):
    """Unregister a webhook URL."""
    try:
        data = await request.json()
        webhook_url = data.get('webhook_url', '')
        
        if not webhook_url:
            return web.json_response({'error': 'webhook_url is required'}, status=400)
        
        if webhook_url in registered_webhooks:
            registered_webhooks.remove(webhook_url)
            logger.info(f"Unregistered webhook: {webhook_url}")
            status = 'success'
        else:
            status = 'not_found'
        
        return web.json_response({
            'status': status,
            'webhook_url': webhook_url,
            'total_webhooks': len(registered_webhooks)
        })
    except Exception as e:
        logger.error(f"Error in unregister_webhook_handler: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def list_webhooks_handler(request):
    """List all registered webhooks."""
    return web.json_response({
        'webhooks': list(registered_webhooks),
        'total': len(registered_webhooks)
    })

async def index_handler(request):
    """Serve a simple HTML page for testing."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebhookMCP Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .section { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; border: 1px solid #ddd; }
            .status { padding: 10px; background: #e3f2fd; border-radius: 4px; margin-bottom: 20px; }
            input, button { padding: 8px; margin: 5px; border-radius: 4px; border: 1px solid #ddd; }
            button { background: #4CAF50; color: white; cursor: pointer; }
            button:hover { background: #45a049; }
            .webhook-list { list-style: none; padding: 0; }
            .webhook-item { padding: 8px; margin: 5px 0; background: white; border-left: 3px solid #2196F3; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔔 WebhookMCP Server</h1>
            <div class="status">
                <strong>Status:</strong> <span style="color: green;">Running ✅</span><br>
                <strong>Registered Webhooks:</strong> <span id="webhookCount">0</span>
            </div>
            
            <div class="section">
                <h2>Register Webhook</h2>
                <input type="text" id="webhookUrl" placeholder="http://localhost:3000/webhook" style="width: 60%;">
                <button onclick="registerWebhook()">Register</button>
                <button onclick="refreshWebhooks()">Refresh List</button>
            </div>
            
            <div class="section">
                <h2>Test Push Message</h2>
                <input type="text" id="testMessage" placeholder="Enter test message" style="width: 60%;">
                <button onclick="pushMessage()">Push Message</button>
            </div>
            
            <div class="section">
                <h2>Registered Webhooks</h2>
                <ul id="webhookList" class="webhook-list">
                    <li>Loading...</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>API Endpoints</h2>
                <pre>
POST /api/register   - Register a webhook
POST /api/unregister - Unregister a webhook
GET  /api/webhooks   - List registered webhooks
POST /api/push       - Push a message to all webhooks
                </pre>
            </div>
        </div>
        <script>
            async function registerWebhook() {
                const url = document.getElementById('webhookUrl').value;
                if (!url) {
                    alert('Please enter a webhook URL');
                    return;
                }
                
                try {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({webhook_url: url})
                    });
                    const data = await response.json();
                    alert(data.status === 'success' ? 'Webhook registered!' : 'Error: ' + data.error);
                    refreshWebhooks();
                } catch (e) {
                    alert('Error: ' + e.message);
                }
            }
            
            async function refreshWebhooks() {
                try {
                    const response = await fetch('/api/webhooks');
                    const data = await response.json();
                    
                    document.getElementById('webhookCount').textContent = data.total;
                    
                    const list = document.getElementById('webhookList');
                    if (data.webhooks.length === 0) {
                        list.innerHTML = '<li>No webhooks registered</li>';
                    } else {
                        list.innerHTML = data.webhooks.map(w => 
                            `<li class="webhook-item">${w} <button onclick="unregisterWebhook('${w}')">Remove</button></li>`
                        ).join('');
                    }
                } catch (e) {
                    alert('Error: ' + e.message);
                }
            }
            
            async function unregisterWebhook(url) {
                try {
                    const response = await fetch('/api/unregister', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({webhook_url: url})
                    });
                    refreshWebhooks();
                } catch (e) {
                    alert('Error: ' + e.message);
                }
            }
            
            async function pushMessage() {
                const message = document.getElementById('testMessage').value;
                if (!message) {
                    alert('Please enter a message');
                    return;
                }
                
                try {
                    const response = await fetch('/api/push', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    const data = await response.json();
                    alert('Message sent to ' + data.webhooks_notified + ' webhook(s)');
                } catch (e) {
                    alert('Error: ' + e.message);
                }
            }
            
            // Initial load
            refreshWebhooks();
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def api_push_handler(request):
    """API endpoint to push messages to registered webhooks."""
    try:
        data = await request.json()
        message = data.get('message', '')
        
        if not message:
            return web.json_response({'error': 'Message is required'}, status=400)
        
        # Send to all webhooks
        success_count = await send_to_all_webhooks(message)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"API push: '{message}' sent to {success_count} webhooks")
        
        return web.json_response({
            'status': 'success',
            'message': message,
            'timestamp': timestamp,
            'webhooks_notified': success_count,
            'total_webhooks': len(registered_webhooks)
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
        web_app.router.add_post('/api/register', register_webhook_handler)
        web_app.router.add_post('/api/unregister', unregister_webhook_handler)
        web_app.router.add_get('/api/webhooks', list_webhooks_handler)
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
async def push_webhook(message: str = "", port: str = "8000", host: str = "0.0.0.0") -> str:
    """Push a message to all registered webhooks via HTTP POST."""
    logger.info(f"Executing push_webhook with message: {message}")
    
    if not message.strip():
        return "❌ Error: Message is required"
    
    try:
        # Parse port
        port_int = int(port) if port.strip() else DEFAULT_PORT
        host_str = host.strip() if host.strip() else DEFAULT_HOST
        
        # Ensure web server is running
        await setup_web_server(port_int, host_str)
        
        # Send to all webhooks
        success_count = await send_to_all_webhooks(message)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        total_webhooks = len(registered_webhooks)
        
        return f"""✅ Message pushed successfully!

📊 Details:
- Message: {message}
- Timestamp: {timestamp}
- Webhooks notified: {success_count}/{total_webhooks}
- Server: http://{host_str}:{port_int}

💡 To manage webhooks, open http://{host_str}:{port_int} in a browser.
💡 Register webhooks via POST to http://{host_str}:{port_int}/api/register with {{"webhook_url": "your_url"}}"""
        
    except ValueError:
        return f"❌ Error: Invalid port number: {port}"
    except Exception as e:
        logger.error(f"Error in push_webhook: {e}")
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
            logger.info(f"✓ Webhook management: http://{DEFAULT_HOST}:{DEFAULT_PORT}/api/webhooks")
            logger.info(f"✓ Dashboard available at http://{DEFAULT_HOST}:{DEFAULT_PORT}")
        else:
            logger.error("Failed to start web server")
            return
        
        # Keep the event loop running forever
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except asyncio.CancelledError:
            logger.info("Web server shutting down...")
            if client_session and not client_session.closed:
                await client_session.close()
    
    try:
        loop.run_until_complete(start_server())
    finally:
        loop.close()

if __name__ == "__main__":
    logger.info("Starting WebhookMCP server (MCP name: 'webhook')...")
    
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
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if client_session and not client_session.closed:
            asyncio.run(client_session.close())
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)