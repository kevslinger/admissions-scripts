import praw

SUBMISSION_ID_PREFIX = "t3_"
COMMENT_ID_PREFIX = "t1_"


def get_user_statistics(reddit: praw.Reddit, username: str):
    """Use Praw to search through a user's history (last 1000 submissions)
    and get statistics like karma per comment, most downvoted stuff, etc."""
    num_comments = 0
    comment_karma = 0

    subreddits = {}
    most_downvoted_comment = None
    most_downvoted_submission = None

    for post in reddit.redditor(username).new(limit=1000):
        post_is_submission = False
        post_is_comment = False
        if post.id.startswith(SUBMISSION_ID_PREFIX):
            # post is a submission
            post_is_submission = True
        elif post.id.startswith(COMMENT_ID_PREFIX):
            # post is a comment
            post_is_comment = True
        else:
            print("Uhhh I've never seen this type of post before. I will skip.")
            continue
        # TODO: is score the same as karma or is it only upvotes?
        # If it's upvotes only I guess we can use score with upvote_ratio to figure out the score
        # Score of 10 and 40% upvote would be like -5 right
        print(f"Score: {post.score}")
        print(f"Link: {post.permalink}")
        if post.subreddit.name not in subreddits:
            subreddits[post.subreddit.name] = 1
        else:
            subreddits[post.subreddit.name] += 1

        if post_is_submission:
            if most_downvoted_submission is None:
                most_downvoted_submission = post
            else:
                num_comments += 1
                comment_karma += post.score
                if post.score < most_downvoted_submission.score:
                    most_downvoted_submission = post
        elif post_is_comment:
            if most_downvoted_comment is None:
                most_downvoted_comment = post
            else:
                if post.score < most_downvoted_comment.score:
                    most_downvoted_comment = post

        top_10_subreddits = [k for k, _ in sorted(subreddits.items(), key=lambda x: x[1], reverse=True)][:10]

    return [comment_karma, num_comments, round(comment_karma / num_comments),
            '?', # Wholesomeness
            top_10_subreddits,
            '?', '?', '?', # Least wholesome Comment/Subreddit/Karma
            most_downvoted_comment, most_downvoted_comment.subreddit.name, most_downvoted_comment.score,
            most_downvoted_submission, most_downvoted_submission.subreddit.name, most_downvoted_submission.score,
            '?' # TODO: Word Cloud
            ]
# Actual comment karma
# Number of comments
# Karma per comment
# Wholesomeness
# Subreddits Frequented
# Least Wholesome Comment/Subreddit/Karma
# Most Downvoted Comment/Subreddit/Karma
# Most Downvoted Post/Subreddit/Karma