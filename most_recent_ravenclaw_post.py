from utils import reddit_utils
from dotenv import load_dotenv
from tqdm import tqdm
import os
import constants
import datetime
import prawcore
import threading
load_dotenv(override=True)


class TowerRecencyGetter:
    def __init__(self, sub_name="ravenclaw"):
        self.reddit_client = reddit_utils.create_reddit_client()
        self.sub_name = sub_name
        self.lock = threading.Lock()

    def get_userset(self, start_idx: int = 0, end_idx: int = 1000):
        """Get all users in r/ravenclaw that have posted within the last year"""
        users_one_year = []
        with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, constants.RECENCY_CSV), 'r') as f:
            lines = f.readlines()
            for line in lines[start_idx:end_idx]:
                toks = line.split(',')
                # Most recent post within 1 year
                if int(toks[1]) < 1:
                    users_one_year.append(toks[0])

        recency_dict = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }
        for username in tqdm(users_one_year):
            redditor = self.reddit_client.redditor(username)
            write_flag = False
            try:
                for post in redditor.new(limit=2000):
                    if post.subreddit == self.sub_name:
                        time_created = datetime.datetime.utcfromtimestamp(int(post.created_utc))
                        if time_created + datetime.timedelta(days=366 * 5) < datetime.datetime.now():
                            delta_years = 5
                            recency_dict[5].append(username)
                            # print(f"{username} has not posted anything publicly in the last 5 years.")
                        elif time_created + datetime.timedelta(days=366 * 4) < datetime.datetime.now():
                            delta_years = 4
                            recency_dict[4].append(username)
                            # print(f"{username} has not posted anything publicly in the last 4 years.")
                        elif time_created + datetime.timedelta(days=366 * 3) < datetime.datetime.now():
                            delta_years = 3
                            recency_dict[3].append(username)
                            # print(f"{username} has not posted anything publicly in the last 3 years.")
                        elif time_created + datetime.timedelta(days=366 * 2) < datetime.datetime.now():
                            delta_years = 2
                            recency_dict[2].append(username)
                            # print(f"{username} has not posted anything publicly in the last 2 years.")
                        elif time_created + datetime.timedelta(days=366 * 1) < datetime.datetime.now():
                            delta_years = 1
                            recency_dict[1].append(username)
                            # print(f"{username} has not posted anything publicly in the last year.")
                        else:
                            delta_years = 0
                            recency_dict[0].append(username)
                        with self.lock:
                            with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, "tower_recency2.csv"), 'a') as csv_file:
                                csv_file.write(f"{username},{delta_years}\n")
                            write_flag = True
                        break
            except prawcore.exceptions.NotFound:
                print(f"{username} is probably banned!")
                continue

            if not write_flag:
                with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, "tower_recency2.csv"), 'a') as csv_file:
                    csv_file.write(f"{username},-1\n")

    def run_threads(self, num_threads=10):
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=self.get_userset, args=(int(i * (11_000/num_threads)),
                                                                     int((i+1) * (11_000/num_threads))))
            threads.append(thread)
            thread.start()


if __name__ == '__main__':
    runner = TowerRecencyGetter()
    runner.run_threads()
