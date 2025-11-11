#!/usr/bin/env node
/**
 * Test script to verify the webstream connection
 * This will attempt to connect and report the status
 */

const { EventSource } = require('eventsource');

const STREAM_URL = 'http://localhost:8000/stream';
let connectionAttempts = 0;
const MAX_ATTEMPTS = 3;

console.log('🧪 WebStream Connection Test\n');
console.log('═'.repeat(60));

function testConnection() {
    connectionAttempts++;
    console.log(`\n📡 Attempt ${connectionAttempts}/${MAX_ATTEMPTS}: Connecting to ${STREAM_URL}`);
    
    const eventSource = new EventSource(STREAM_URL);
    let timeout;
    let receivedData = false;

    // Set a timeout for connection
    timeout = setTimeout(() => {
        console.log('⏱️  Connection timeout (5 seconds)');
        eventSource.close();
        
        if (connectionAttempts < MAX_ATTEMPTS) {
            console.log('🔄 Retrying...');
            setTimeout(testConnection, 2000);
        } else {
            console.log('\n' + '═'.repeat(60));
            console.log('❌ TEST FAILED: Could not connect to webstream\n');
            console.log('📋 Possible reasons:');
            console.log('   1. Docker container not running');
            console.log('   2. Web server not started yet (starts on first push_stream call)');
            console.log('   3. Port 8000 is blocked or in use by another service\n');
            console.log('💡 Next steps:');
            console.log('   1. Verify container is running: docker-compose ps');
            console.log('   2. Check container logs: docker-compose logs');
            console.log('   3. The web server starts when you first call push_stream');
            console.log('   4. Try asking Claude to "Push test message to the webstream"\n');
            process.exit(1);
        }
    }, 5000);

    eventSource.onopen = () => {
        clearTimeout(timeout);
        console.log('✅ Connection successful!');
        console.log('⏳ Waiting for initial message...');
    };

    eventSource.onmessage = (event) => {
        if (!receivedData) {
            receivedData = true;
            clearTimeout(timeout);
            console.log('📨 Received data:', event.data);
            console.log('\n' + '═'.repeat(60));
            console.log('✅ TEST PASSED: Webstream is working correctly!\n');
            console.log('🎉 Your listener can now receive messages.');
            console.log('💡 Start the listener with: node stream-listener.js\n');
            eventSource.close();
            process.exit(0);
        }
    };

    eventSource.onerror = (error) => {
        clearTimeout(timeout);
        
        if (error.status === 404) {
            console.log('❌ Error: 404 - Endpoint not found');
        } else if (error.status === 0) {
            console.log('❌ Error: Connection refused');
        } else if (error.message) {
            console.log('❌ Error:', error.message);
        } else {
            console.log('❌ Error: Connection failed');
        }
        
        eventSource.close();
        
        if (connectionAttempts < MAX_ATTEMPTS) {
            console.log('🔄 Retrying in 2 seconds...');
            setTimeout(testConnection, 2000);
        } else {
            console.log('\n' + '═'.repeat(60));
            console.log('❌ TEST FAILED: Could not establish connection\n');
            console.log('📋 The MCP server might be waiting for the first push_stream call');
            console.log('   The web server (port 8000) starts on-demand when:');
            console.log('   - Someone calls the push_stream tool via MCP');
            console.log('   - Claude is asked to push a message to the stream\n');
            console.log('💡 To start the web server:');
            console.log('   1. Configure Claude Desktop with this MCP server');
            console.log('   2. Ask Claude: "Push test message to the webstream"');
            console.log('   3. Then run this test again\n');
            process.exit(1);
        }
    };
}

// Start the test
testConnection();

