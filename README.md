# MCP Reddit Client

A Python application that uses PRAW to fetch and display Reddit posts and comments from your custom feed.

## Setup

1. Make sure you have Python 3.13 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -e .
   ```
3. Configure your Reddit API credentials in the `.env` file:
   - `REDDIT_CLIENT_ID`: Your Reddit application client ID
   - `REDDIT_CLIENT_SECRET`: Your Reddit application client secret
   - `REDDIT_USERNAME`: Your Reddit username
   - `REDDIT_PASSWORD`: Your Reddit password

## Usage

Run the application:
```bash
python api.py
```

The application will:
1. Fetch posts from your home feed
2. Display each post with its title, author, score, and content
3. Fetch and display comments for each post

## Features

- View posts from your home feed
- View posts from specific subreddits
- View comments and their replies
- Beautiful console output with formatting
- Markdown support for post content

## API Methods

The `RedditClient` class provides the following methods:

- `get_home_feed(limit=10)`: Get posts from your home feed
- `get_subreddit_posts(subreddit, limit=10)`: Get posts from a specific subreddit
- `get_post_comments(post_id, limit=10)`: Get comments from a specific post
- `display_post(post)`: Display a formatted post
- `display_comment(comment)`: Display a formatted comment
