import os
import prawcore
import datetime
import sys
sys.path.append('.')
from utils import reddit_utils

"""Get the list of contributors in r/ravenclaw and save them to a txt file. You can also save the 
    Suspended/banned users in a separate text file if you wish to purge them, which we've done in the past.
"""

def main():
    reddit = reddit_utils.create_reddit_client()

    for contributor in reddit.subreddit('ravenclaw').contributor(limit=None):
        try:
            # Get the user out of lazy loading I guess?
            if contributor.has_subscribed is False:
                pass
            with open(os.path.join(os.getcwd(), 'output_files', f"ravenclaw_contributors_{datetime.datetime.now().strftime('%m_%d_%y')}.txt"), 'a') as f:
                f.write(f"{contributor.name}\n")
        except AttributeError:
            print(f"{contributor.name} has been suspended")
            continue
        except prawcore.exceptions.NotFound:
            print(f"Is {contributor} suspended? They have been banned or some shit")
            continue


if __name__ == '__main__':
    main()
