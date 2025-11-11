import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WebStream Listener',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const WebStreamListenerPage(),
    );
  }
}

class WebStreamListenerPage extends StatefulWidget {
  const WebStreamListenerPage({super.key});

  @override
  State<WebStreamListenerPage> createState() => _WebStreamListenerPageState();
}

class _WebStreamListenerPageState extends State<WebStreamListenerPage> {
  final List<String> _messages = [];
  String _connectionStatus = 'Disconnected';
  StreamSubscription? _streamSubscription;
  int _eventCount = 0;

  // For web/desktop: use localhost
  // For iOS simulator: use localhost (works on iOS simulator)
  // For Android emulator: use 10.0.2.2
  // For physical device: use your computer's IP address (e.g., '192.168.1.100')
  final String _streamUrl = 'http://localhost:8000/stream';

  @override
  void initState() {
    super.initState();
    _connectToStream();
  }

  @override
  void dispose() {
    _streamSubscription?.cancel();
    super.dispose();
  }

  Future<void> _connectToStream() async {
    setState(() {
      _connectionStatus = 'Connecting...';
      _eventCount = 0;
    });

    try {
      final client = http.Client();
      final request = http.Request('GET', Uri.parse(_streamUrl));

      // Set SSE headers
      request.headers['Accept'] = 'text/event-stream';
      request.headers['Cache-Control'] = 'no-cache';

      final response = await client.send(request);

      if (response.statusCode == 200) {
        setState(() {
          _connectionStatus = 'Connected ✓';
        });

        String buffer = '';

        _streamSubscription = response.stream
            .transform(utf8.decoder)
            .listen(
              (String chunk) {
                buffer += chunk;

                // Process complete lines
                final lines = buffer.split('\n');
                buffer = lines.last; // Keep incomplete line in buffer

                for (int i = 0; i < lines.length - 1; i++) {
                  final line = lines[i].trim();

                  // Parse SSE format: "data: message content"
                  if (line.startsWith('data:')) {
                    final message = line.substring(5).trim();
                    if (message.isNotEmpty) {
                      setState(() {
                        _eventCount++;
                        _messages.insert(
                          0,
                          message,
                        ); // Add to top for newest first
                      });
                    }
                  }
                  // Ignore keepalive comments (lines starting with ':')
                  // and empty lines
                }
              },
              onError: (error) {
                setState(() {
                  _connectionStatus = 'Error: $error';
                });
                // Auto-reconnect after error
                Future.delayed(const Duration(seconds: 3), _connectToStream);
              },
              onDone: () {
                setState(() {
                  _connectionStatus = 'Disconnected';
                });
                // Auto-reconnect on disconnect
                Future.delayed(const Duration(seconds: 3), _connectToStream);
              },
            );
      } else {
        setState(() {
          _connectionStatus = 'Error: HTTP ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _connectionStatus = 'Error: $e';
      });
      // Auto-reconnect on error
      Future.delayed(const Duration(seconds: 5), _connectToStream);
    }
  }

  void _reconnect() {
    _streamSubscription?.cancel();
    setState(() {
      _messages.clear();
      _eventCount = 0;
    });
    _connectToStream();
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
        title: const Text('WebStream Listener'),
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
            color: _connectionStatus == 'Connected'
                ? Colors.green.shade100
                : _connectionStatus.startsWith('Error')
                ? Colors.red.shade100
                : Colors.orange.shade100,
            child: Row(
              children: [
                Icon(
                  _connectionStatus == 'Connected'
                      ? Icons.check_circle
                      : _connectionStatus.startsWith('Error')
                      ? Icons.error
                      : Icons.pending,
                  color: _connectionStatus == 'Connected'
                      ? Colors.green
                      : _connectionStatus.startsWith('Error')
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
                          color: _connectionStatus == 'Connected ✓'
                              ? Colors.green.shade900
                              : _connectionStatus.startsWith('Error')
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
                  _streamUrl.replaceAll('http://', ''),
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
                          'Waiting for messages from the stream...',
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
