import os
import sys
sys.path.append('.')
from utils import reddit_utils
import argparse
from dotenv import load_dotenv
load_dotenv(override=True)

"""Opens up 'names_to_be_removed.txt' and removes each user from your sub
    Stores the list of successfully removed users in purged_users.txt, and all
    Failed to remove users in failed_removals.txt
    requires using the --go flag to actually remove the users, otherwise it will just print out the 
    list of names to be removed
"""


def main(args):
    reddit_client = reddit_utils.create_reddit_client()
    ravenclaw_sub = reddit_client.subreddit("ravenclaw")

    user_list = []
    with open(os.path.join(os.getcwd(), "names_to_be_removed.txt"), 'r') as f:
        lines = f.readlines()
        for line in lines:
            user_list.append(line.replace('\n', ''))

    if args.go:
        for user in user_list:
            try:
                reddit_account = reddit_client.redditor(user)
                ravenclaw_sub.contributor.remove(reddit_account)
                print(user)
                with open(os.path.join(os.getcwd(), "output_files/purged_users.txt"), 'a') as f:
                    f.write(f"{user}\n")
            except Exception:
                with open(os.path.join(os.getcwd(), "output_files/failed_removals.txt"), 'a') as f:
                    f.write(f"{user}\n")
    else:
        print("Dry Run")
        print("Here are the users that will be removed:")
        print(chr(10).join(user_list))
        print(f"There are {len(user_list)} users to be removed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--go', action='store_true')

    main(parser.parse_args())
