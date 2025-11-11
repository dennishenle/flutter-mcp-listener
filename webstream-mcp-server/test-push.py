#!/usr/bin/env python3
"""
Quick test script to push a message to the webstream
This simulates what happens when the push_stream MCP tool is called
"""
import asyncio
import sys
from datetime import datetime, timezone
from aiohttp import web
import aiohttp

async def push_message(message: str, port: int = 8000, host: str = "localhost"):
    """Push a message directly to the running web server's stream clients."""
    print(f"🚀 Pushing message to webstream...")
    print(f"📝 Message: {message}")
    print(f"🌐 Target: http://{host}:{port}")
    print()
    
    # The webstream server doesn't have an API endpoint to push messages
    # Instead, we'll demonstrate by showing the message format that would be sent
    timestamp = datetime.now(timezone.utc).isoformat()
    formatted_message = f"[{timestamp}] {message}"
    
    print(f"✅ Message would be formatted as:")
    print(f"   data: {formatted_message}")
    print()
    print(f"📡 To receive this message:")
    print(f"   1. Your listener at: node stream-listener.js")
    print(f"   2. Your browser at: http://localhost:8000")
    print()
    print("💡 Note: The current MCP server design requires messages to be")
    print("   pushed through the MCP protocol (stdio), not via HTTP API.")

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "Hello from Cursor!"
    asyncio.run(push_message(message))

