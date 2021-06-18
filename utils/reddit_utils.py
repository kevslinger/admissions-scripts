import praw
import os
from datetime import datetime


def create_reddit_client() -> praw.Reddit:
    """Initialize AsyncPraw reddit api"""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=f"{os.getenv('REDDIT_USERNAME')} Bot",
        username=os.getenv("REDDIT_USERNAME"),
    )


def get_formatted_time() -> str:
    """Get time and format it to be human readable"""
    return datetime.strftime(datetime.now(), '%B %d, %Y %H:%M:%S')


def convert_reddit_timestamp(time) -> str:
    """Convert from unix time to human-readable"""
    return datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
