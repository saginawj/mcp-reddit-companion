[![smithery badge](https://smithery.ai/badge/@saginawj/mcp-reddit-companion)](https://smithery.ai/server/@saginawj/mcp-reddit-companion)

# MCP Reddit Companion

A Reddit companion tool built with MCP that allows you to read custom feeds and post comments.

## Features

- Read posts from custom feeds (multireddits)
- View comments from specific posts
- Read posts from all custom feeds at once

## Prerequisites

- Python 3.11+
- Reddit API credentials (client ID, client secret, username, password)
- Docker (optional, for containerized deployment)

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-reddit.git
cd mcp-reddit
```

2. Install dependencies using uv:
```bash
uv pip install .
```

3. Create a `.env` file with your Reddit API credentials:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t mcp-reddit .
```

2. Run the container (for passwords with special characters):
```bash
docker run \
  -e REDDIT_CLIENT_ID='your_client_id' \
  -e REDDIT_CLIENT_SECRET='your_client_secret' \
  -e REDDIT_USERNAME='your_username' \
  -e REDDIT_PASSWORD='your_password' \
  mcp-reddit
```

Note: If your password contains special characters (like !, $, etc.), make sure to:
1. Use single quotes around the password
2. Escape any special characters with a backslash
3. Or use double quotes and escape the special characters

Example with special characters:
```bash
docker run \
  -e REDDIT_CLIENT_ID='your_client_id' \
  -e REDDIT_CLIENT_SECRET='your_client_secret' \
  -e REDDIT_USERNAME='your_username' \
  -e REDDIT_PASSWORD='your\!password' \
  mcp-reddit
```

## Usage

### Local Usage

1. Start the MCP server:
```bash
uv run mcp dev src/mcp_reddit_companion/server.py
```

2. Use the available tools:
- Get posts from a custom feed:
```python
get_custom_feed("feed_name", limit=5)
```

- Get comments from a post:
```python
get_post_comments("post_id", limit=10)
```

- Get posts from all custom feeds:
```python
read_custom_feeds(limit_per_feed=5)
```

### Docker Usage

The MCP server will start automatically when the container runs. You can interact with it through your MCP client.

## Configuration

### Cursor Integration

To use with Cursor, add the following to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "reddit-companion": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\code\\personal\\mcp-reddit",
        "run",
        "mcp",
        "dev",
        "src/mcp_reddit_companion/server.py"
      ]
    }
  }
}
```

## License

MIT
