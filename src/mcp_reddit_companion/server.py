import os
from typing import List, Optional
import praw
from dotenv import load_dotenv
from fastmcp import FastMCP
import logging
import asyncio

# Load environment variables
load_dotenv()

# Create MCP server
mcp = FastMCP("Reddit MCP")
client = None
logging.getLogger().setLevel(logging.WARNING)

@mcp.tool()
async def get_custom_feed(feed_name: str, limit: int = 10) -> str:
    """
    Get posts from a custom feed (multireddit)
    
    Args:
        feed_name: Name of the custom feed (e.g., "thought_garden")
        limit: Number of posts to fetch (default: 10)
        
    Returns:
        Human readable string containing list of post information
    """
    try:
        global client
        if client is None:
            client = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                user_agent="mcp-reddit/0.1.0"
            )

        posts = []
        # Get all multireddits and find the one with matching name
        for multireddit in client.user.me().multireddits():
            if multireddit.name == feed_name:
                for submission in multireddit.hot(limit=limit):
                    post_info = (
                        f"Title: {submission.title}\n"
                        f"Subreddit: r/{submission.subreddit.display_name}\n"
                        f"Score: {submission.score}\n"
                        f"Author: {submission.author}\n"
                        f"URL: {submission.url}\n"
                        f"Link: https://reddit.com{submission.permalink}\n"
                        f"---"
                    )
                    posts.append(post_info)
                break
        else:
            return f"Multireddit '{feed_name}' not found"

        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def get_post_comments(post_id: str, limit: int = 10) -> str:
    """
    Get comments from a specific post
    
    Args:
        post_id: Reddit post ID
        limit: Number of top-level comments to fetch (default: 10)
        
    Returns:
        Human readable string containing post content and comments
    """
    try:
        global client
        if client is None:
            client = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                user_agent="mcp-reddit/0.1.0"
            )

        submission = client.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        
        content = (
            f"Title: {submission.title}\n"
            f"Subreddit: r/{submission.subreddit.display_name}\n"
            f"Score: {submission.score}\n"
            f"Author: {submission.author}\n"
            f"URL: {submission.url}\n"
            f"Link: https://reddit.com{submission.permalink}\n"
        )

        if submission.selftext:
            content += f"\nContent:\n{submission.selftext}\n"

        content += "\nComments:\n"
        for comment in submission.comments.list()[:limit]:
            content += _format_comment(comment)

        return content

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

def _format_comment(comment, depth: int = 0) -> str:
    """Helper method to recursively format comment tree with proper indentation"""
    indent = "  " * depth
    content = (
        f"{indent}* Author: {comment.author}\n"
        f"{indent}  Score: {comment.score}\n"
        f"{indent}  {comment.body}\n"
    )

    for reply in comment.replies:
        content += _format_comment(reply, depth + 1)

    return content

if __name__ == "__main__":
    mcp.run(transport="stdio")