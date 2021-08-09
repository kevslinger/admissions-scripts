from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import constants
from utils import google_utils, praw_utils, reddit_utils, redditmetis_utils
import gspread
import time
import os
import praw
from dotenv import load_dotenv
load_dotenv()


def main():
    # Get the sheet key from ENV (requires setting env or having a .env)
    SHEET_KEY = os.getenv("SHEET_KEY")
    # Get the Google Sheets client
    gspread_client = google_utils.create_gspread_client()
    # Open the Google Sheet
    sheet = gspread_client.open_by_key(SHEET_KEY)
    # Get the specific spreadsheet tab
    admissions_tab = sheet.worksheet(constants.FORM_TAB_NAME)
    python_tab = sheet.worksheet(constants.DATA_TAB_NAME)
    # Set the options for our chrome driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    # Get the Chrome Driver
    driver = webdriver.Chrome(executable_path=constants.CHROMEDRIVER_PATH,
                              options=chrome_options)

    # Call the function to look through each of the new rows on the sheet
    start_col = "A"
    end_col = "X"
    reddit_client = reddit_utils.create_reddit_client()
    update_sheet(driver, reddit_client, admissions_tab, python_tab, start_col, end_col)


def update_sheet(driver: webdriver, reddit_client: praw.Reddit, form_tab: gspread.Worksheet, data_tab: gspread.Worksheet, start_col: str, end_col: str) -> None:
    """
    :param driver: Chrome webdriver from Selenium, used to pull up redditmetis info
    :param reddit_client: The praw client (used if redditmetis does not work)
    :param form_tab: The google sheets tab connected to the admissions form
    :param data_tab: The google sheets tab we'll put the values in
    :param start_col: The first column to store values in
    :param end_col: The last column to store values in
    """
    is_redditmetis_down = False
    # STEP 1: FIND THE ROW TO START AT
    # STEP 2: START PROCESSING FROM THAT ROW ONWARDS
    # Loop through each row in the sheet from the back (we only care about new entries)
    for idx, row in reversed(list(enumerate(form_tab.get_all_values()))):
        # skip header
        if idx < 1:
            return
        #    continue
        # Check to see if USERNAME column is empty.
        # TODO: is this the best way to check?
        if row[1] == "":
            continue
        # Get the row's username
        username = row[1]
        # Check to see if the username is already in the sheet
        search_results = data_tab.findall(username, in_column=2)
        # For each match, check to see if the timestamps match
        # If the timestamps match, that means we're caught up
        # TODO: this is not ideal
        dupe_flag = False
        for result in search_results:
            if data_tab.cell(result.row, result.col-1).value == row[0]:
                dupe_flag = True
                break
        if dupe_flag:
            break
    # idx tracks the most recently filled out row in the form responses that we have not yet processed
    # we need to increment by 1 because google sheets is 1-indexed while python is 0-indexed
    idx += 1
    # data_tab_row_idx is the index of the first open row where we should output our processed info
    data_tab_row_idx = google_utils.get_next_row(data_tab)
    # Keep looping until we've processed all new users
    while True:
        # Bump to new row
        idx += 1
        try:
            # Our form has 6 values - timestamp, username, karma, previous house, and 2 short answers
            row = form_tab.row_values(idx)[:6]
        except IndexError:
            break
        # If we get to an empty row, we're done
        if row[1] == "":
            break
        username = row[1]
        # Get the URL to open up with chrome
        user_url = f"{constants.REDDITMETIS_URL}{username}"
        results = []
        # This one time redditmetis was down for like 24 hours and I'm still scarred from that
        if not is_redditmetis_down:
            try:
                driver.get(user_url)

                # Wait 5 seconds for the page to load TODO: different time?
                time.sleep(5)
                # Pulls in all the info we need about the reddit user
                # If the redditmetis page fails or hasn't loaded yet, results will be None
                results = redditmetis_utils.get_stats(driver)
                # This fails mechanism will on average let us speed up how long it takes for each person
                # If the page hasn't finished loading, we wait 10 seconds, then 15 seconds, then 30 seconds.
                # If the page still hasn't loaded by then (50 total seconds), we'll assume there was some error
                # If the user has never made a public *post* (praw submission), they will not show up on redditmetis I think
                fails = 3

                while not results and fails > 0:
                    print(f"Failed! {fails} fails remaining")
                    results = redditmetis_utils.get_stats(driver)
                    time.sleep(30 / fails)
                    fails -= 1
            # Redditmetis is down, need to do my own praw analysis
            except TimeoutException:
                is_redditmetis_down = True

        # If redditmetis goes down or the user does not have info on redditmetis, we'll do our own praw analysis
        if is_redditmetis_down or not results:
            # You can disable the praw analysis and just put a bunch of quetion marks, which is what I
            # did in a previous version.
            results = praw_utils.get_user_statistics(reddit_client, username)

        row += results
        # Add reddit account overview and redditmetis account overview links
        row.append(f"{constants.REDDIT_URL}user/{username}")
        row.append(user_url)
        # This is for the checkbox I have which we check to TRUE when we add the user
        row.append("FALSE")
        # Update the appropriate row with the info
        # Need to do idx + 1 because google sheets are 1-indexed while python is 0-indexed
        # raw=False allows us to do =HYPERLINK which we used for Most Downvoted, etc.
        data_tab.update(f'{start_col}{data_tab_row_idx}:{end_col}{data_tab_row_idx}', [row], raw=False)
        data_tab_row_idx += 1


if __name__ == '__main__':
    main()
