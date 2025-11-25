import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shelf/shelf.dart' as shelf;
import 'package:shelf/shelf_io.dart' as shelf_io;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Webhook Listener',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const WebhookListenerPage(),
    );
  }
}

class WebhookListenerPage extends StatefulWidget {
  const WebhookListenerPage({super.key});

  @override
  State<WebhookListenerPage> createState() => _WebhookListenerPageState();
}

class _WebhookListenerPageState extends State<WebhookListenerPage> {
  final List<String> _messages = [];
  String _connectionStatus = 'Starting...';
  int _eventCount = 0;
  HttpServer? _server;

  // Local HTTP server configuration
  final int _localPort = 3000;

  // MCP server configuration
  // For web/desktop: use localhost
  // For iOS simulator: use localhost (works on iOS simulator)
  // For Android emulator: use 10.0.2.2
  // For physical device: use your computer's IP address (e.g., '192.168.1.100')
  final String _mcpServerUrl = 'http://192.168.0.47:8000';

  String get _webhookUrl {
    // For the webhook registration, we need to use a URL that the MCP server can reach
    // On macOS/iOS simulator: use 'localhost'
    // On Android emulator: the host machine is accessible at 10.0.2.2
    // For physical devices: use your computer's actual IP address
    if (Platform.isAndroid) {
      // When running on Android emulator, localhost on the emulator means the emulator itself
      // The host machine is at 10.0.2.2
      return 'http://10.0.2.2:$_localPort/webhook';
    } else {
      // For iOS simulator and desktop, localhost works
      return 'http://192.168.0.47:$_localPort/webhook';
    }
  }

  @override
  void initState() {
    super.initState();
    _startWebhookServer();
  }

  @override
  void dispose() {
    _stopServer();
    super.dispose();
  }

  Future<void> _startWebhookServer() async {
    setState(() {
      _connectionStatus = 'Starting server...';
    });

    try {
      // Create a Shelf handler for webhook requests
      final handler = const shelf.Pipeline()
          .addMiddleware(shelf.logRequests())
          .addHandler(_handleWebhookRequest);

      // Start the HTTP server
      _server = await shelf_io.serve(
        handler,
        InternetAddress.anyIPv4,
        _localPort,
      );

      setState(() {
        _connectionStatus = 'Server running on :$_localPort';
      });

      debugPrint('Webhook server started on port $_localPort');

      // Register webhook with MCP server
      await _registerWebhook();
    } catch (e) {
      setState(() {
        _connectionStatus = 'Error starting server: $e';
      });
      debugPrint('Error starting webhook server: $e');
    }
  }

  Future<shelf.Response> _handleWebhookRequest(shelf.Request request) async {
    // Only accept POST requests to /webhook
    if (request.method != 'POST' || request.url.path != 'webhook') {
      return shelf.Response.notFound('Not found');
    }

    try {
      // Read the request body
      final body = await request.readAsString();
      final data = json.decode(body) as Map<String, dynamic>;

      final message = data['message'] as String?;
      final timestamp = data['timestamp'] as String?;

      if (message != null) {
        // Update UI with the received message
        setState(() {
          _eventCount++;
          _messages.insert(0, '[$timestamp] $message');
        });

        debugPrint('Received webhook: $message');

        return shelf.Response.ok(
          json.encode({'status': 'success', 'received': message}),
          headers: {'Content-Type': 'application/json'},
        );
      } else {
        return shelf.Response.badRequest(
          body: json.encode({'error': 'Message field is required'}),
        );
      }
    } catch (e) {
      debugPrint('Error handling webhook: $e');
      return shelf.Response.internalServerError(
        body: json.encode({'error': e.toString()}),
      );
    }
  }

  Future<void> _registerWebhook() async {
    try {
      final response = await http.post(
        Uri.parse('$_mcpServerUrl/api/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'webhook_url': _webhookUrl}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _connectionStatus = 'Registered ✓ (port $_localPort)';
        });
        debugPrint('Webhook registered successfully');
      } else {
        setState(() {
          _connectionStatus = 'Registration failed: ${response.statusCode}';
        });
        debugPrint('Failed to register webhook: ${response.body}');
      }
    } catch (e) {
      setState(() {
        _connectionStatus = 'Registration error: $e';
      });
      debugPrint('Error registering webhook: $e');
    }
  }

  Future<void> _unregisterWebhook() async {
    try {
      await http.post(
        Uri.parse('$_mcpServerUrl/api/unregister'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'webhook_url': _webhookUrl}),
      );
      debugPrint('Webhook unregistered');
    } catch (e) {
      debugPrint('Error unregistering webhook: $e');
    }
  }

  Future<void> _stopServer() async {
    await _unregisterWebhook();
    await _server?.close(force: true);
    _server = null;
  }

  void _reconnect() async {
    await _stopServer();
    setState(() {
      _messages.clear();
      _eventCount = 0;
    });
    await _startWebhookServer();
  }

  void _clearMessages() {
    setState(() {
      _messages.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Webhook Listener'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep),
            tooltip: 'Clear messages',
            onPressed: _clearMessages,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Reconnect',
            onPressed: _reconnect,
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            color: _connectionStatus.contains('✓')
                ? Colors.green.shade100
                : _connectionStatus.startsWith('Error') ||
                      _connectionStatus.contains('failed')
                ? Colors.red.shade100
                : Colors.orange.shade100,
            child: Row(
              children: [
                Icon(
                  _connectionStatus.contains('✓')
                      ? Icons.check_circle
                      : _connectionStatus.startsWith('Error') ||
                            _connectionStatus.contains('failed')
                      ? Icons.error
                      : Icons.pending,
                  color: _connectionStatus.contains('✓')
                      ? Colors.green
                      : _connectionStatus.startsWith('Error') ||
                            _connectionStatus.contains('failed')
                      ? Colors.red
                      : Colors.orange,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Status: $_connectionStatus',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _connectionStatus.contains('✓')
                              ? Colors.green.shade900
                              : _connectionStatus.startsWith('Error') ||
                                    _connectionStatus.contains('failed')
                              ? Colors.red.shade900
                              : Colors.orange.shade900,
                        ),
                      ),
                      if (_eventCount > 0)
                        Text(
                          'Events received: $_eventCount',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade700,
                          ),
                        ),
                    ],
                  ),
                ),
                Text(
                  'Port $_localPort',
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade700),
                ),
              ],
            ),
          ),
          Expanded(
            child: _messages.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.message_outlined,
                          size: 64,
                          color: Colors.grey.shade400,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'No messages yet',
                          style: TextStyle(
                            fontSize: 18,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Waiting for webhook messages...',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    itemCount: _messages.length,
                    reverse: false,
                    padding: const EdgeInsets.all(8),
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      final eventNumber = _eventCount - index;

                      return Card(
                        margin: const EdgeInsets.symmetric(
                          vertical: 4,
                          horizontal: 8,
                        ),
                        elevation: 2,
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: Theme.of(
                              context,
                            ).colorScheme.primary,
                            child: Text(
                              '$eventNumber',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                              ),
                            ),
                          ),
                          title: Text(
                            message,
                            style: const TextStyle(fontSize: 14),
                          ),
                          subtitle: Text(
                            'Event #$eventNumber',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
