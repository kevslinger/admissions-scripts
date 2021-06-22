import praw
import prawcore
import datetime
import time
import csv
import os
import threading
import matplotlib.pyplot as plt
from utils import reddit_utils
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(override=True)

OUTPUT_DIR = "output_files"
MAIN_TEXT_FILE = "ravenclaw_contributors.txt"
SHADOWBANNED = "ravenclaw_shadowbanned.txt"
UNVERIFIED = "unverified.txt"
UNSUBSCRIBED = "unsubscribed.txt"
RECENCY_CSV = "ravenclaw_recency.csv"


class SubredditAnalyzer:
    def __init__(self, sub_name="ravenclaw"):
        self.reddit_client = reddit_utils.create_reddit_client()
        self.subreddit = self.reddit_client.subreddit(sub_name)
        self.lock = threading.Lock()
        # TODO: Ideally, I think I would increment a version or something.
        if os.path.exists(os.path.join(os.getcwd(), OUTPUT_DIR, MAIN_TEXT_FILE)):
            os.rm(os.path.join(os.getcwd(), OUTPUT_DIR, MAIN_TEXT_FILE))
        if os.path.exists(os.path.join(os.getcwd(), OUTPUT_DIR, SHADOWBANNED)):
            os.rm(os.path.join(os.getcwd(), OUTPUT_DIR, SHADOWBANNED))
        if os.path.exists(os.path.join(os.getcwd(), OUTPUT_DIR, UNVERIFIED)):
            os.rm(os.path.join(os.getcwd(), OUTPUT_DIR, UNVERIFIED))
        if os.path.exists(os.path.join(os.getcwd(), OUTPUT_DIR, UNSUBSCRIBED)):
            os.rm(os.path.join(os.getcwd(), OUTPUT_DIR, UNSUBSCRIBED))
        if os.path.exists(os.path.join(os.getcwd(), OUTPUT_DIR, RECENCY_CSV)):
            os.rm(os.path.join(os.getcwd(), OUTPUT_DIR, RECENCY_CSV))

    def get_random_facts(self) -> str:
        """Get some random statistics for fun"""
        sub_time_created = reddit_utils.convert_reddit_timestamp(self.subreddit.created_utc)
        sub_description = self.subreddit.public_description
        sub_count = self.subreddit.subscribers
        sub_name = self.subreddit.display_name
        num_banned = 0
        banned_users = []
        for ban in self.subreddit.banned():
            num_banned += 1
            banned_users.append(f"{ban}: {ban.note}")
        return f"{sub_name} was created on {sub_time_created}. It has {sub_count} subscribers, and its " \
               f"public description is {sub_description}. There are {num_banned} banned users in {sub_name}:\n" \
               f"{chr(10).join(banned_users)}"

    def get_contributors(self, start_idx=0, end_idx=1000):
        """Iterate through the subreddit's contributors and get number of banned/suspended/shadowbanned,
        As well as when each contributor's last (public) post was"""
        print(start_idx)
        print(end_idx)
        num_contributors = 0
        contributors = []
        shadowbanneds = []
        unverifieds = []
        unsubscribeds = []
        num_unverified = 0
        num_unsubscribed = 0
        num_suspended_or_banned = 0
        years_since_last_post = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
        }
        #checkpoint_time = time.time()

        for contributor in tqdm(self.subreddit.contributor(limit=end_idx), total=end_idx):
            if num_contributors <= start_idx - 1:
                num_contributors += 1
                continue
            #print(f"{num_contributors}: {contributor}")
            num_contributors += 1
            #if not num_contributors % 10:
            #    print(f"[ {datetime.datetime.now().strftime('%B %d, %H:%M:%S')} ] Checkpoint: {num_contributors - start_idx} "
            #          f"contributors processed in {time.time() - checkpoint_time} seconds.")
            #    checkpoint_time = time.time()
            try:
                if contributor.verified is False:
                    num_unverified += 1
                    unverifieds.append(contributor.name)
                    with self.lock:
                        with open(os.path.join(os.getcwd(), OUTPUT_DIR, UNVERIFIED), "a") as f:
                            f.write(f"{contributor.name}\n")
                    continue
                if contributor.has_subscribed is False:
                    num_unsubscribed += 1
                    unsubscribeds.append(contributor.name)
                    with self.lock:
                        with open(os.path.join(os.getcwd(), OUTPUT_DIR, UNSUBSCRIBED), "a") as f:
                            f.write(f"{contributor.name}\n")
                    continue
            except AttributeError:
                num_suspended_or_banned += 1
                shadowbanneds.append(contributor.name)
                with self.lock:
                    with open(os.path.join(os.getcwd(), OUTPUT_DIR, SHADOWBANNED), "a") as f:
                        f.write(f"{contributor.name}\n")
                continue
            except prawcore.exceptions.NotFound:
                print(f"Is {contributor} suspended? {contributor.is_suspended}. They have been banned or some shit")
                num_suspended_or_banned += 1
                shadowbanneds.append(contributor.name)
                continue
            for most_recent_post in contributor.new(limit=1):
                time_created = datetime.datetime.utcfromtimestamp(int(most_recent_post.created_utc))
                if time_created + datetime.timedelta(days=366*5) < datetime.datetime.now():
                    delta_years = 5
                    years_since_last_post[5].append(contributor)
                    # print(f"{contributor} has not posted anything publicly in the last 5 years.")
                elif time_created + datetime.timedelta(days=366 * 4) < datetime.datetime.now():
                    delta_years = 4
                    years_since_last_post[4].append(contributor)
                    # print(f"{contributor} has not posted anything publicly in the last 4 years.")
                elif time_created + datetime.timedelta(days=366 * 3) < datetime.datetime.now():
                    delta_years = 3
                    years_since_last_post[3].append(contributor)
                    # print(f"{contributor} has not posted anything publicly in the last 3 years.")
                elif time_created + datetime.timedelta(days=366 * 2) < datetime.datetime.now():
                    delta_years = 2
                    years_since_last_post[2].append(contributor)
                    # print(f"{contributor} has not posted anything publicly in the last 2 years.")
                elif time_created + datetime.timedelta(days=366 * 1) < datetime.datetime.now():
                    delta_years = 1
                    years_since_last_post[1].append(contributor)
                    # print(f"{contributor} has not posted anything publicly in the last year.")
                else:
                    delta_years = 0
                    years_since_last_post[0].append(contributor)
                with self.lock:
                    with open(os.path.join(os.getcwd(), OUTPUT_DIR, RECENCY_CSV), 'a') as csv_file:
                        csv_file.write(f"{contributor.name},{delta_years}\n")
            contributors.append(contributor.name)
            with self.lock:
                with open(os.path.join(os.getcwd(), OUTPUT_DIR, MAIN_TEXT_FILE), "a") as f:
                    f.write(f"{contributor.name}\n")


    def run_threads(self, num_threads=12):
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=self.get_contributors, args=(i * (12_000/num_threads), (i+1) * (12_000/num_threads)))
            threads.append(thread)
            thread.start()


if __name__ == '__main__':
    analyzer = SubredditAnalyzer()
    print(analyzer.get_random_facts())
    #analyzer.run_threads(num_threads=12)

# print(f"According to praw, I count {num_contributors} members of {sub_name}.")
# print(f"The list of contributors has {len(contributors)} entries in it.")
# print(f"We can remove duplicates, which gives us {len(list(set(contributors)))} users.")
# print(f"The number of unverified subscribers is {num_unverified}")
# print(f"The number of unsubscribed users is {num_unsubscribed}")
# print(f"The number of suspended, banned, or shadowbanned users is {num_suspended_or_banned}")
#
# fig, ax = plt.subplots()
# ax.bar(range(len(years_since_last_post), years_since_last_post.values()))
# ax.set_xlabel("Years")
# ax.set_ylabel("Users")
# ax.set_title("Last (public) post recency among users in r/ravenclaw")
# plt.savefig(os.path.join(os.getcwd(), "most_recent_post_bars.png"))
