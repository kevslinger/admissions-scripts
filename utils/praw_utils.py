import praw

SUBMISSION_ID_PREFIX = "t3_"
COMMENT_ID_PREFIX = "t1_"


def get_user_statistics(reddit: praw.Reddit, username: str):
    """Use Praw to search through a user's history (last 1000 submissions)
    and get statistics like karma per comment, most downvoted stuff, etc."""
    num_comments = 0

    subreddits = {}
    most_downvoted_comment = None
    most_downvoted_submission = None

    reddit_user = reddit.redditor(username)
    comment_karma = reddit_user.comment_karma


    for post in reddit_user.new(limit=1000):
        post_is_submission = False
        post_is_comment = False
        if post.fullname.startswith(SUBMISSION_ID_PREFIX):
            # post is a submission
            post_is_submission = True
        elif post.fullname.startswith(COMMENT_ID_PREFIX):
            # post is a comment
            post_is_comment = True
        else:
            print("Uhhh I've never seen this type of post before. I will skip.")
            continue
        # TODO: is score the same as karma or is it only upvotes?
        # If it's upvotes only I guess we can use score with upvote_ratio to figure out the score
        # Score of 10 and 40% upvote would be like -5 right
        if post.subreddit.name not in subreddits:
            subreddits[post.subreddit.display_name] = 1
        else:
            subreddits[post.subreddit.display_name] += 1

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

    top_10_subreddits = [f"r/{k}" for k, _ in sorted(subreddits.items(), key=lambda x: x[1], reverse=True)][:10]

    return [comment_karma, num_comments, round(comment_karma / num_comments) if num_comments > 0 else 0,
            '?', # Wholesomeness
            ','.join(top_10_subreddits) if top_10_subreddits else '?',
            '?', '?', '?', # Least wholesome Comment/Subreddit/Karma
            f'=HYPERLINK("https://www.reddit.com{most_downvoted_comment.permalink}", "{most_downvoted_comment.body}")' if most_downvoted_comment is not None else 'N/A',
            f"r/{most_downvoted_comment.subreddit.display_name}" if most_downvoted_comment is not None else 'N/A',
            most_downvoted_comment.score if most_downvoted_comment is not None else 'N/A',
            f'=HYPERLINK("https://www.reddit.com{most_downvoted_submission.permalink}", "{most_downvoted_submission.selftext}")' if most_downvoted_submission is not None else 'N/A',
            f"r/{most_downvoted_submission.subreddit.display_name}" if most_downvoted_submission is not None else 'N/A',
            most_downvoted_submission.score if most_downvoted_submission is not None else 'N/A',
            '?' # TODO: Word Cloud
            ]
