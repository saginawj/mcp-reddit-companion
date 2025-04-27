import os
import logging
from typing import Optional
from dotenv import load_dotenv
import praw
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Set logging level
logging.basicConfig(level=logging.WARNING)

# Initialize MCP server
mcp = FastMCP("Reddit MCP")

# === Client Helper ===
def get_reddit_client() -> praw.Reddit:
    """
    Creates an authenticated Reddit client using refresh token only.
    Login/password is no longer supported.
    """
    logger = logging.getLogger(__name__)

    refresh_token = os.getenv("REDDIT_REFRESH_TOKEN")
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if not all([refresh_token, client_id, client_secret]):
        logger.error("❌ Missing required Reddit OAuth credentials.")
        raise ValueError("REDDIT_REFRESH_TOKEN, CLIENT_ID, and CLIENT_SECRET are all required.")

    logger.info("🔐 Using Reddit OAuth via refresh_token")
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        user_agent="mcp-reddit/0.2.0"
    )

# === Helper Functions ===

def format_submission(submission) -> str:
    """Format Reddit submission data for display."""
    return (
        f"Title: {submission.title}\n"
        f"Subreddit: r/{submission.subreddit.display_name}\n"
        f"Score: {submission.score}\n"
        f"Author: {submission.author}\n"
        f"URL: {submission.url}\n"
        f"Link: https://reddit.com{submission.permalink}\n---"
    )

def _format_comment(comment, depth: int = 0) -> str:
    """Format Reddit comment data for display, including replies."""
    indent = "  " * depth
    content = (
        f"{indent}* Author: {comment.author}\n"
        f"{indent}  Score: {comment.score}\n"
        f"{indent}  {comment.body}\n"
    )
    for reply in comment.replies:
        content += _format_comment(reply, depth + 1)
    return content


# === Tools ===

@mcp.tool()
async def get_custom_feed(feed_name: str, limit: int = 10) -> str:
    try:
        client = get_reddit_client()
        posts = []
        for multireddit in client.user.me().multireddits():
            if multireddit.name == feed_name:
                for submission in multireddit.hot(limit=limit):
                    posts.append(format_submission(submission))
                break
        else:
            return f"Multireddit '{feed_name}' not found"
        return "\n\n".join(posts)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def get_post_comments(post_id: str, limit: int = 10) -> str:
    try:
        client = get_reddit_client()
        submission = client.submission(id=post_id)
        submission.comments.replace_more(limit=0)
        content = format_submission(submission)
        if submission.selftext:
            content += f"\nContent:\n{submission.selftext}\n"
        content += "\nComments:\n"
        for comment in submission.comments.list()[:limit]:
            content += _format_comment(comment)
        return content
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def read_custom_feeds() -> str:
    try:
        client = get_reddit_client()
        all_posts = []
        for multireddit in client.user.me().multireddits():
            all_posts.append(f"\n=== Posts from feed: {multireddit.name} ===\n")
            for submission in multireddit.hot():
                all_posts.append(format_submission(submission))
        return "\n".join(all_posts) if all_posts else "No custom feeds found"
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def read_new_posts(limit: int = 20) -> str:
    try:
        client = get_reddit_client()
        posts = [f"\n=== Latest Posts ===\n"]
        for submission in client.subreddit("all").new(limit=limit):
            posts.append(format_submission(submission))
        return "\n".join(posts) if posts else "No posts found"
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_user_activity(limit: int = 20) -> str:
    try:
        client = get_reddit_client()
        activity = ["\n=== Your Recent Activity ===\n\nRecent Posts:\n"]
        for submission in client.user.me().submissions.new(limit=limit // 2):
            activity.append(format_submission(submission))
        activity.append("\nRecent Comments:\n")
        for comment in client.user.me().comments.new(limit=limit // 2):
            activity.append(
                f"Subreddit: r/{comment.subreddit.display_name}\n"
                f"Score: {comment.score}\n"
                f"Comment: {comment.body[:200]}...\n"
                f"Link: https://reddit.com{comment.permalink}\n---\n"
            )
        return "\n".join(activity)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_post_engagement(post_id: Optional[str] = None, limit: int = 5) -> str:
    try:
        client = get_reddit_client()
        if post_id:
            submission = client.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            result = (
                f"\n=== Post Engagement Metrics ===\n"
                f"{format_submission(submission)}\n"
                f"Upvote Ratio: {submission.upvote_ratio * 100:.1f}%\n"
                f"Total Comments: {submission.num_comments}\n"
                f"Views: {getattr(submission, 'view_count', 'N/A')}\n"
                f"Created: {submission.created_utc}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"\nRecent Comments:\n"
            )
            for comment in submission.comments.list()[:10]:
                result += _format_comment(comment)
            return result
        else:
            result = "\n=== Recent Posts Engagement ===\n"
            for submission in client.user.me().submissions.new(limit=limit):
                submission.comments.replace_more(limit=0)
                result += (
                    f"{format_submission(submission)}\n"
                    f"Upvote Ratio: {submission.upvote_ratio * 100:.1f}%\n"
                    f"Total Comments: {submission.num_comments}\n"
                    f"Views: {getattr(submission, 'view_count', 'N/A')}\n"
                    f"Created: {submission.created_utc}\n"
                    f"Link: https://reddit.com{submission.permalink}\n"
                    f"Top Comments:\n"
                )
                for comment in submission.comments.list()[:3]:
                    result += _format_comment(comment)
                result += "\n---\n"
            return result
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_unread_messages(limit: int = 10) -> str:
    try:
        client = get_reddit_client()
        messages = ["\n=== Unread Messages ===\n"]
        for message in client.inbox.unread(limit=limit):
            messages.append(
                f"From: {message.author}\n"
                f"Subject: {message.subject}\n"
                f"Body: {message.body}\n"
                f"Created: {message.created_utc}\n---\n"
            )
            message.mark_read()
        return "\n".join(messages) if messages else "No unread messages"
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_saved_items(limit: int = 10) -> str:
    client = get_reddit_client()
    saved = []
    for item in client.user.me().saved(limit=limit):
        if isinstance(item, praw.models.Submission):
            saved.append(f"[Post] {item.title} (r/{item.subreddit}) — {item.url}")
        elif isinstance(item, praw.models.Comment):
            saved.append(f"[Comment] in r/{item.subreddit} — {item.body[:100]}")
    return "\n".join(saved) if saved else "No saved items found."

@mcp.tool()
def get_subscribed_subreddits(limit: int = 20) -> str:
    client = get_reddit_client()
    return "\n".join(
        f"r/{sub.display_name} — {sub.title}" 
        for sub in client.user.subreddits(limit=limit)
    )

@mcp.tool()
def get_upvoted(limit: int = 10) -> str:
    client = get_reddit_client()
    return "\n".join(
        f"{item.title} (r/{item.subreddit}) — {item.url}"
        for item in client.user.me().upvoted(limit=limit)
    )

# === Entry Point ===

if __name__ == "__main__":
    mcp.run(transport="stdio")
