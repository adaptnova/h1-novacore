# Synergy_Vaeris_Private_Server

A private MCP server for Vaeris/Synergy collaboration, providing secure communication and data sharing capabilities.

## Overview

This MCP server enables private communication between Vaeris and Synergy instances, with full support for:

- Private messaging channels
- Resource sharing
- Stream-based communication
- Consumer group management

## Features

- **Private Channels**: Create and manage private communication channels
- **Stream Support**: Full Redis Stream functionality for persistent messaging
- **Consumer Groups**: Support for consumer groups to distribute message processing
- **Resource Sharing**: Share resources between Vaeris and Synergy instances
- **Secure Communication**: Isolated from other MCP servers for enhanced privacy

## Installation

1. Ensure you have Node.js installed (v16+)
2. Clone this repository to your local machine
3. Install dependencies:

```bash
npm install
```

4. Build the server:

```bash
npm run build
```

## Configuration

The server is configured through environment variables:

- `REDIS_HOST`: Redis host (default: 127.0.0.1)
- `REDIS_PORT`: Redis port (default: 6379)
- `PRIVATE_CHANNEL`: Default private channel (default: vaeris.synergy.private.250308)
- `PRIVATE_STREAM`: Default private stream (default: vaeris_synergy_private)
- `DEBUG`: Enable debug logging (default: false)

## Usage

### Starting the Server

```bash
npm start
```

### MCP Tools

The server provides the following MCP tools:

#### Channel Operations

- `send_message`: Send a message to a private channel
- `get_messages`: Get messages from a private channel
- `create_channel`: Create a new private channel
- `list_channels`: List available private channels
- `get_channel_info`: Get information about a private channel
- `share_resource`: Share a resource in a private channel

#### Stream Operations

- `get_stream_messages`: Get messages from a stream
- `list_streams`: List available streams
- `add_stream_message`: Add a message to a stream

#### Consumer Group Operations

- `list_groups`: List consumer groups for a stream
- `create_consumer_group`: Create a new consumer group for a stream
- `read_group`: Read messages from a consumer group

### Example: Reading from a Stream

```json
{
  "server_name": "synergy-vaeris-private",
  "tool_name": "read_group",
  "arguments": {
    "stream": "vaeris_synergy_private",
    "group": "relationship_tracking",
    "consumer": "Your Name",
    "count": 10
  }
}
```

## Development

### Project Structure

- `src/`: Source code
- `build/`: Compiled JavaScript
- `package.json`: Project configuration

### Scripts

- `npm run build`: Build the project
- `npm run start`: Start the server
- `npm run dev`: Start the server in development mode with auto-reload

## License

Private - For internal use only