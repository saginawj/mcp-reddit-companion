import os
from typing import List, Optional
import praw
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

class RedditClient:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="mcp-reddit/0.1.0"
        )
        self.console = Console()

    def get_home_feed(self, limit: int = 10) -> List[praw.models.Submission]:
        """Get posts from your home feed."""
        return list(self.reddit.front.hot(limit=limit))

    def get_custom_feed(self, feed_name: str, limit: int = 10) -> List[praw.models.Submission]:
        """Get posts from a custom feed (multireddit)."""
        # For your own multireddits
        if "/me/" in feed_name:
            feed_name = feed_name.split("/")[-1]
            # Get all multireddits and find the one with matching name
            for multireddit in self.reddit.user.me().multireddits():
                if multireddit.name == feed_name:
                    return list(multireddit.hot(limit=limit))
            raise ValueError(f"Multireddit '{feed_name}' not found")
        # For other users' multireddits
        else:
            username, feed_name = feed_name.split("/")
            # Get all multireddits and find the one with matching name
            for multireddit in self.reddit.multireddits(username=username):
                if multireddit.name == feed_name:
                    return list(multireddit.hot(limit=limit))
            raise ValueError(f"Multireddit '{feed_name}' not found for user '{username}'")

    def get_subreddit_posts(self, subreddit: str, limit: int = 10) -> List[praw.models.Submission]:
        """Get posts from a specific subreddit."""
        return list(self.reddit.subreddit(subreddit).hot(limit=limit))

    def get_post_comments(self, post_id: str, limit: int = 10) -> List[praw.models.Comment]:
        """Get comments from a specific post."""
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Remove MoreComments objects
        return list(submission.comments.list())[:limit]

    def display_post(self, post: praw.models.Submission):
        """Display a post with formatting."""
        self.console.print("\n[bold blue]Post:[/bold blue]")
        self.console.print(f"[bold]{post.title}[/bold]")
        self.console.print(f"Subreddit: r/{post.subreddit.display_name}")
        self.console.print(f"Author: {post.author}")
        self.console.print(f"Score: {post.score}")
        self.console.print(f"URL: {post.url}")
        if post.selftext:
            self.console.print(Markdown(post.selftext))

    def display_comment(self, comment: praw.models.Comment, level: int = 0):
        """Display a comment with formatting."""
        indent = "  " * level
        self.console.print(f"\n{indent}[bold green]Comment:[/bold green]")
        self.console.print(f"{indent}Author: {comment.author}")
        self.console.print(f"{indent}Score: {comment.score}")
        self.console.print(f"{indent}{comment.body}")
        for reply in comment.replies:
            self.display_comment(reply, level + 1)

def main():
    client = RedditClient()
    
    # Example usage
    # print("Fetching posts from home feed...")
    # posts = client.get_home_feed(limit=5)
    
    # for post in posts:
    #     client.display_post(post)
        
    #     # Get and display comments for each post
    #     print("\nFetching comments...")
    #     comments = client.get_post_comments(post.id, limit=3)
    #     for comment in comments:
    #         client.display_comment(comment)

    # Example of using custom feed
    print("\nFetching posts from a custom feed...")
    # Replace with your custom feed name
    # Format: "username/feedname" for other users' feeds
    # Format: "/me/feedname" for your own feeds
    custom_feed_posts = client.get_custom_feed("/me/thought_garden", limit=5)
    for post in custom_feed_posts:
        client.display_post(post)

if __name__ == "__main__":
    main()
