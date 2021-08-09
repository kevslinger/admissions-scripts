from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import constants
from utils import google_utils, praw_utils, reddit_utils, redditmetis_utils
import gspread
import time
import os
import string
import requests
import praw
from tqdm import tqdm
import prawcore
import threading
from dotenv import load_dotenv
load_dotenv(override=True)

"""PLEASE DO NOT LOOK AT THIS
    honestly I'm just not even gonna try to comment it or explain it
    But I backfilled every user in the tower with a redditmetis analysis
    Which took like 12 hours I think.
"""


class SubredditScrubber:
    def __init__(self):
        # Get the sheet key from ENV (requires setting env or having a .env)
        SHEET_KEY = os.getenv("SCRUB_SHEET_KEY")
        # Get the Google Sheets client
        gspread_client = google_utils.create_gspread_client()
        # Open the Google Sheet
        sheet = gspread_client.open_by_key(SHEET_KEY)
        # Get the specific spreadsheet tab
        self.backfill_tab = sheet.worksheet("Backfill")
        self.suspended_tab = sheet.worksheet("Suspended")
        self.redditmetis_error_tab = sheet.worksheet("redditmetis_errors")

        self.main_lock = threading.Lock()
        self.suspended_lock = threading.Lock()
        self.file_lock = threading.Lock()

        contributor_file = open(os.path.join(os.getcwd(), "output_files", "redditmetis_errors.txt"), "r")
        self.lines = [line.replace('\n', '') for line in contributor_file.readlines()]

        # Call the function to look through each of the new rows on the sheet
        self.start_col = "B"
        self.end_col = "R"
        self.reddit_client = reddit_utils.create_reddit_client()

    def update_sheet(self, driver: webdriver.Chrome, start_idx: int, end_idx: int) -> None:
        """
        :param driver: The Google Chrome webdriver
        :param start_idx: The redditor index to start from (for multithreading)
        :param end_idx: The redditor index to end with (for multithreading)
        """
        is_redditmetis_down = False
        # Loop through users in the sub
        with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, "processed_users.txt"), 'r') as f:
            processed_users = [line.replace('\n', '') for line in f.readlines()]
        num_contributors = 0
        #for contributor in tqdm(ravenclaw_sub.contributor(limit=end_idx), total=end_idx):
        for username in tqdm(self.lines):
            # skip header
            if num_contributors <= start_idx - 1:
                num_contributors += 1
                continue
            if num_contributors >= end_idx:
                break
            # Skip names we've already done
            if username in processed_users:
                continue
            num_contributors += 1
            contributor = self.reddit_client.redditor(username)
            try:
                # Get the user out of lazy loading I guess?
                if contributor.has_subscribed is False:
                    pass
            except AttributeError:
                with self.suspended_lock:
                    self.suspended_tab.append_row([f"{contributor.name}"])
                print(f"{contributor.name} has been suspended")
                continue
            except prawcore.exceptions.NotFound:
                print(f"Is {contributor} suspended? They have been banned or some shit")
                with self.suspended_lock:
                    self.suspended_tab.append_row([f"{contributor.name}"])
                continue
            # Get the URL to open up with chrome
            user_url = f"{constants.REDDITMETIS_URL}{contributor.name}"
            comment_karma = -1
            results = []
            row = [contributor.name]
            if not is_redditmetis_down:
                try:
                    driver.get(user_url)

                    # Wait 5 seconds for the page to load TODO: different time?
                    time.sleep(5)
                    # Pulls in all the info we need about the reddit user
                    results = redditmetis_utils.get_stats(driver)
                    # This fails mechanism will on average let us speed up how long it takes for each person
                    # If the page hasn't finished loading, we wait 10 seconds, then 15 seconds, then 30 seconds.
                    # If the page still hasn't loaded by then (50 total seconds), we'll assume there was some error
                    fails = 3

                    while not results and fails > 0:
                        #print(f"Failed! {fails} fails remaining")
                        results = redditmetis_utils.get_stats(driver)
                        time.sleep(30 / fails)
                        fails -= 1
                        # Reddit hits you with a "429: Too many messages" error seemingly often.
                        # I threw this block in here because I want it to wait, too, so makes sense
                        # To do the same waiting as opposed to re-configuring a fail/wait block.
                        if comment_karma < 0:
                            # If we can't find their results, look them up on the static reddit user about page.
                            user_info = requests.get(f"{constants.REDDIT_URL}user/{contributor.name}/about.json")
                            if user_info.status_code == requests.codes.OK:
                                try:
                                    # If the user does not exist or is banned or something, they'll still return a 200 but
                                    # Won't have the comment_karma field.
                                    comment_karma = user_info.json()['data']['comment_karma']
                                except KeyError:
                                    pass
                # Redditmetis is down, need to do my own praw analysis
                except TimeoutException:
                    is_redditmetis_down = True

            # If redditmetis goes down, we'll do our own praw analysis
            if is_redditmetis_down or not results:
                # TODO: For now, don't do praw stuff. too slow, we can backfill later offline
                #with self.file_lock:
                #    with open(os.path.join(os.getcwd(), "output_files", "redditmetis_errors.txt"), "a") as f:
                #        f.write(f"{contributor.name}\n")
                results = praw_utils.get_user_statistics(self.reddit_client, contributor.name)

            # Could not get results after waiting for so long. Assume user causes an error on redditmetis
            # TODO: Maybe we should wait even longer? Just slows down the code though.
            if not results:
                #print(f"User {contributor.name} cannot be found on {constants.REDDITMETIS_URL}{contributor.name}!")
                # If we found their comment karma on the ABOUT page, then put it on the results list
                if comment_karma >= 0:
                    row.append(comment_karma)
                else:
                    # Otherwise, we know nothing about them.
                    row.append('?')
                # Add filler to the sheet
                # TODO: We do -3 because we then add the reddit and redditmetis links as well as the checkbox
                row += ['?'] * (string.ascii_uppercase.index(self.end_col) - string.ascii_uppercase.index(self.start_col) - 3)
            else:
                row += results
            # Add reddit account overview and redditmetis account overview links
            row.append(f"{constants.REDDIT_URL}user/{contributor.name}")
            row.append(user_url)

            # TODO: What are the good boundaries for flagging
            # Wholesomeness at most 50% or least wholesome / most downvoted comment at most -50
            # try:
            #     if int(row[4][:-1]) <= 50 or int(row[8]) <= -50 or int(row[11]) <= -50:
            #         with self.lock:
            #             self.flagged_tab.append_row(row, value_input_option='USER_ENTERED')
            #     else:
            #         with self.lock:
            #             self.unflagged_tab.append_row(row, value_input_option='USER_ENTERED')
            # except ValueError:
            #     # If this is the case, maybe we don't have wholesomeness (e.g. praw) but we do have
            #     # most downvoted comment
            #     if int(row[11]) <= -50:
            #         with self.lock:
            #             self.flagged_tab.append_row(row, value_input_option='USER_ENTERED')
            #     else:
            #         with self.lock:
            #             self.unflagged_tab.append_row(row, value_input_option='USER_ENTERED')
            with self.main_lock:
                #self.backfill_tab.append_row(row, value_input_option='USER_ENTERED')
                self.redditmetis_error_tab.append_row(row, value_input_option='USER_ENTERED')
            # Update the appropriate row with the info
            # Need to do idx + 1 because google sheets are 1-indexed while python is 0-indexed
            # raw=False allows us to do =HYPERLINK which we used for Most Downvoted, etc.
            # sheet_tab.update(f'{start_col}{idx + 1}:{end_col}{idx + 1}', [results], raw=False)
            # data_tab.append_row(row, value_input_option='USER_ENTERED')
            #data_tab.update(f'A{data_tab_row_idx}:{end_col}{data_tab_row_idx}', [row], raw=False)
            #data_tab_row_idx += 1
            with self.file_lock:
                with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, "processed_users.txt"), 'a') as f:
                    f.write(f"{contributor.name}\n")

    def run_threads(self, num_threads=12):
        threads = []
        for i in range(num_threads):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.binary_location = constants.GOOGLE_CHROME_PATH
            # Get the Chrome Driver
            driver = webdriver.Chrome(executable_path=constants.CHROMEDRIVER_PATH,
                                      options=chrome_options)
            thread = threading.Thread(target=self.update_sheet, args=(driver, i * (11_000/num_threads), (i+1) * (11_000/num_threads)))
            threads.append(thread)
            thread.start()


if __name__ == '__main__':
    scrubber = SubredditScrubber()
    #scrubber.run_threads(num_threads=11)
    scrubber.update_sheet(None, 0, 10_000)