import praw
import prawcore

SUBMISSION_ID_PREFIX = "t3_"
COMMENT_ID_PREFIX = "t1_"


def get_user_statistics(reddit: praw.Reddit, username: str):
    """Use Praw to search through a user's history (last 1000 submissions)
    and get statistics like karma per comment, most downvoted stuff, etc.
    ONLY USED WHEN REDDITMETIS IS DOWN OR HAS NO PROFILE FOR SOMEONE
    Arguments:
        reddit: (praw's Reddit instance) our reddit account
        username: (str) the username of the person we are trying to analyze"""

    num_comments = 0

    subreddits = {}
    most_downvoted_comment = None
    most_downvoted_submission = None

    try:
        # Use praw to look up the user's reddit account
        reddit_user = reddit.redditor(username)
        comment_karma = reddit_user.comment_karma
    
        for post in reddit_user.new(limit=1000):
            post_is_submission = post.fullname.startswith(SUBMISSION_ID_PREFIX)
            post_is_comment = post.fullname.startswith(COMMENT_ID_PREFIX)
            # Can only handle posts and comments. Haven't seen this before but just want to be safe just in case
            if not post_is_submission and not post_is_comment:
                print("Uhhh I've never seen this type of post before. I will skip.")
                continue
            # Keep track of the subreddits the user is active in, with frequency
            if post.subreddit.name not in subreddits:
                subreddits[post.subreddit.display_name] = 1
            else:
                subreddits[post.subreddit.display_name] += 1
            # TODO: is score the same as karma or is it only upvotes?
            if post_is_submission:
                if most_downvoted_submission is None:
                    most_downvoted_submission = post
                else:
                    if post.score < most_downvoted_submission.score:
                        most_downvoted_submission = post
            elif post_is_comment:
                num_comments += 1
                if most_downvoted_comment is None:
                    most_downvoted_comment = post
                else:
                    if post.score < most_downvoted_comment.score:
                        most_downvoted_comment = post

        top_10_subreddits = ", ".join([f"r/{k}" for k, _ in sorted(subreddits.items(), key=lambda x: x[1], reverse=True)][:10])

        # The output is formally:
        # comment karma
        # number of reddit comments (up to 1000)
        # average karma per comment (if the user has more than 1000 comments this number is wrong but that's ok)
        # Wholesomeness (not implemented yet but we need to match the redditmetis output)
        # Least wholesome comment link (not implemented)
        # Least wholesome comment karma (not implemented)
        # Least wholesome comment subreddit (not implemented)
        # Most downvoted COMMENT link
        # Most downvoted COMMENT karma
        # Most downvoted COMMENT subreddit
        # Most downvoted POST link
        # Most downvoted POST karma
        # Most downvoted POST subreddit
        # Top 10 most frequented subreddits (last 1000 comments)
        # Word cloud (not implemented)
        return [comment_karma, num_comments, round(comment_karma / num_comments) if num_comments > 0 else 0,
                '?', # Wholesomeness
                top_10_subreddits if top_10_subreddits else '?',
                '?', '?', '?', # Least wholesome Comment/Subreddit/Karma
                f'=HYPERLINK("https://www.reddit.com{most_downvoted_comment.permalink}", "{most_downvoted_comment.body}")' if most_downvoted_comment is not None else 'N/A',
                f"r/{most_downvoted_comment.subreddit.display_name}" if most_downvoted_comment is not None else 'N/A',
                most_downvoted_comment.score if most_downvoted_comment is not None else 'N/A',
                f'=HYPERLINK("https://www.reddit.com{most_downvoted_submission.permalink}", "{most_downvoted_submission.selftext}")' if most_downvoted_submission is not None else 'N/A',
                f"r/{most_downvoted_submission.subreddit.display_name}" if most_downvoted_submission is not None else 'N/A',
                most_downvoted_submission.score if most_downvoted_submission is not None else 'N/A',
                '?' # TODO: Word Cloud
                ]
    # Usually this happens when someone typos their username
    except prawcore.exceptions.NotFound:
        return ["is", "this", "user",
                "banned",
                "because",
                "I", "cannot", "find",
                "anything",
                "about",
                "them",
                "on",
                "redditmetis",
                "or",
                "praw"]
