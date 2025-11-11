// Simple Node.js client to listen to the WebstreamMCP SSE stream
// Install required package: npm install eventsource

const { EventSource } = require('eventsource');

// Configuration
const STREAM_URL = 'http://localhost:8000/stream';

console.log('🌐 WebstreamMCP Client Starting...');
console.log(`📡 Connecting to: ${STREAM_URL}\n`);

// Create EventSource connection
const eventSource = new EventSource(STREAM_URL);

// Track connection state
let eventCount = 0;
let isConnected = false;

// Handle successful connection
eventSource.onopen = () => {
    isConnected = true;
    console.log('✅ Connected to webstream!');
    console.log('⏳ Waiting for messages...\n');
    console.log('─'.repeat(60));
};

// Handle incoming messages
eventSource.onmessage = (event) => {
    eventCount++;
    const timestamp = new Date().toLocaleTimeString();

    console.log(`\n📨 Event #${eventCount} received at ${timestamp}`);
    console.log(`📝 Data: ${event.data}`);
    console.log('─'.repeat(60));
};

// Handle errors
eventSource.onerror = (error) => {
    if (isConnected) {
        console.error('\n❌ Connection lost!');
        isConnected = false;
    } else {
        console.error('\n❌ Failed to connect to stream');
        console.error('Make sure the WebstreamMCP server is running on port 8000');
    }

    // Log error details if available
    if (error.message) {
        console.error(`Error: ${error.message}`);
    }

    console.log('\n🔄 EventSource will automatically attempt to reconnect...\n');
};

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n👋 Shutting down client...');
    eventSource.close();
    console.log('✅ Disconnected from webstream');
    console.log(`📊 Total events received: ${eventCount}`);
    process.exit(0);
});

// Keep the process running
console.log('\n💡 Press Ctrl+C to stop listening\n');