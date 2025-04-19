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

@mcp.tool()
def read_custom_feeds() -> str:
    """
    Get posts from all custom feeds (multireddits)
    
    Args:
        limit_per_feed: Number of posts to fetch from each feed (default: 5)
        
    Returns:
        Human readable string containing posts from all custom feeds
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

        all_posts = []
        # Get all multireddits
        for multireddit in client.user.me().multireddits():
            feed_name = multireddit.name
            all_posts.append(f"\n=== Posts from feed: {feed_name} ===\n")
            
            # Get posts from this feed
            for submission in multireddit.hot():
                post_info = (
                    f"Title: {submission.title}\n"
                    f"Subreddit: r/{submission.subreddit.display_name}\n"
                    f"Score: {submission.score}\n"
                    f"Author: {submission.author}\n"
                    f"URL: {submission.url}\n"
                    f"Link: https://reddit.com{submission.permalink}\n"
                    f"---"
                )
                all_posts.append(post_info)

        if not all_posts:
            return "No custom feeds found"

        return "\n".join(all_posts)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def read_new_posts(limit: int = 20) -> str:
    """
    Get the latest posts from Reddit
    
    Args:
        limit: Number of posts to fetch (default: 20)
        
    Returns:
        Human readable string containing the latest posts
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

        all_posts = []
        all_posts.append("\n=== Latest Posts ===\n")
        
        # Get latest posts from all subreddits
        for submission in client.subreddit("all").new(limit=limit):
            post_info = (
                f"Title: {submission.title}\n"
                f"Subreddit: r/{submission.subreddit.display_name}\n"
                f"Score: {submission.score}\n"
                f"Author: {submission.author}\n"
                f"URL: {submission.url}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            all_posts.append(post_info)

        if not all_posts:
            return "No posts found"

        return "\n".join(all_posts)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_user_activity(limit: int = 20) -> str:
    """
    Get the user's recent activity including posts and comments
    
    Args:
        limit: Number of items to fetch (default: 20)
        
    Returns:
        Human readable string containing user's recent activity
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

        activity = []
        activity.append("\n=== Your Recent Activity ===\n")
        
        # Get recent posts
        activity.append("\nRecent Posts:\n")
        for submission in client.user.me().submissions.new(limit=limit//2):
            post_info = (
                f"Title: {submission.title}\n"
                f"Subreddit: r/{submission.subreddit.display_name}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.num_comments}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            activity.append(post_info)

        # Get recent comments
        activity.append("\nRecent Comments:\n")
        for comment in client.user.me().comments.new(limit=limit//2):
            comment_info = (
                f"Subreddit: r/{comment.subreddit.display_name}\n"
                f"Score: {comment.score}\n"
                f"Comment: {comment.body[:200]}...\n"
                f"Link: https://reddit.com{comment.permalink}\n"
                f"---"
            )
            activity.append(comment_info)

        if not activity:
            return "No recent activity found"

        return "\n".join(activity)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_post_engagement(post_id: Optional[str] = None, limit: int = 5) -> str:
    """
    Get detailed engagement metrics for posts
    
    Args:
        post_id: Optional Reddit post ID. If not provided, gets engagement for recent posts
        limit: Number of recent posts to analyze if post_id is not provided (default: 5)
        
    Returns:
        Human readable string containing post engagement metrics
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

        if post_id:
            # Get engagement for specific post
            submission = client.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            engagement_info = (
                f"\n=== Post Engagement Metrics ===\n"
                f"Title: {submission.title}\n"
                f"Subreddit: r/{submission.subreddit.display_name}\n"
                f"Score: {submission.score}\n"
                f"Upvote Ratio: {submission.upvote_ratio * 100:.1f}%\n"
                f"Total Comments: {submission.num_comments}\n"
                f"Views: {getattr(submission, 'view_count', 'N/A')}\n"
                f"Created: {submission.created_utc}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
            )

            # Get recent comments
            engagement_info += "\nRecent Comments:\n"
            for comment in submission.comments.list()[:10]:
                engagement_info += _format_comment(comment)

            return engagement_info
        else:
            # Get engagement for recent posts
            engagement_info = "\n=== Recent Posts Engagement ===\n"
            
            for submission in client.user.me().submissions.new(limit=limit):
                submission.comments.replace_more(limit=0)
                
                post_metrics = (
                    f"\nTitle: {submission.title}\n"
                    f"Subreddit: r/{submission.subreddit.display_name}\n"
                    f"Score: {submission.score}\n"
                    f"Upvote Ratio: {submission.upvote_ratio * 100:.1f}%\n"
                    f"Total Comments: {submission.num_comments}\n"
                    f"Views: {getattr(submission, 'view_count', 'N/A')}\n"
                    f"Created: {submission.created_utc}\n"
                    f"Link: https://reddit.com{submission.permalink}\n"
                )
                
                # Get top comments
                post_metrics += "\nTop Comments:\n"
                for comment in submission.comments.list()[:3]:
                    post_metrics += _format_comment(comment)
                
                engagement_info += post_metrics + "\n---\n"

            return engagement_info

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_unread_messages(limit: int = 10) -> str:
    """
    Get unread messages and notifications
    
    Args:
        limit: Number of messages to fetch (default: 10)
        
    Returns:
        Human readable string containing unread messages
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

        messages = []
        messages.append("\n=== Unread Messages ===\n")
        
        for message in client.inbox.unread(limit=limit):
            message_info = (
                f"From: {message.author}\n"
                f"Subject: {message.subject}\n"
                f"Body: {message.body}\n"
                f"Created: {message.created_utc}\n"
                f"---"
            )
            messages.append(message_info)
            # Mark as read
            message.mark_read()

        if not messages:
            return "No unread messages"

        return "\n".join(messages)

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