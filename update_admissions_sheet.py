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
    #chrome_options.binary_location = constants.GOOGLE_CHROME_PATH
    # Get the Chrome Driver
    driver = webdriver.Chrome(executable_path=constants.CHROMEDRIVER_PATH,
                              options=chrome_options)

    # Call the function to look through each of the new rows on the sheet
    start_col = "G"
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
    #for idx, row in enumerate(form_tab.get_all_values()):
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
    # idx tracks the most recently filled out row
    # we need to increment by 1 because google sheets is 1-indexed while python is 0-indexed
    idx += 1
    # NOW: start from idx+1 row, go until we get to an empty row
    data_tab_row_idx = google_utils.get_next_row(data_tab)
    while True:
        # Bump to new row
        idx += 1
        try:
            row = form_tab.row_values(idx)[:6]
        except IndexError:
            break
        # If we get to an empty row, we're done
        if row[1] == "":
            break
        # Both Timestamp and username are empty, check if the python columns are empty as well
        # TODO: This is kinda hacky
        # If two columns are full, we've already processed it, so we're done.
        #if row[6] != "" and row[7] != "":
        #    break
        username = row[1]
        # Get the URL to open up with chrome
        user_url = f"{constants.REDDITMETIS_URL}{username}"
        comment_karma = -1
        results = []
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
                    print(f"Failed! {fails} fails remaining")
                    results = redditmetis_utils.get_stats(driver)
                    time.sleep(30 / fails)
                    fails -= 1
                    # Reddit hits you with a "429: Too many messages" error seemingly often.
                    # I threw this block in here because I want it to wait, too, so makes sense
                    # To do the same waiting as opposed to re-configuring a fail/wait block.
                    if comment_karma < 0:
                        # If we can't find their results, look them up on the static reddit user about page.
                        user_info = requests.get(f"{constants.REDDIT_URL}user/{username}/about.json")
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
            results = praw_utils.get_user_statistics(reddit_client, username)

        # Could not get results after waiting for so long. Assume user causes an error on redditmetis
        # TODO: Maybe we should wait even longer? Just slows down the code though.
        if not results:
            print(f"User {row[1]} cannot be found on {constants.REDDITMETIS_URL}{username}!")
            # If we found their comment karma on the ABOUT page, then put it on the results list
            if comment_karma >= 0:
                row.append(comment_karma)
            else:
                # Otherwise, we know nothing about them.
                row.append('?')
            # Add filler to the sheet
            # TODO: We do -3 because we then add the reddit and redditmetis links as well as the checkbox
            row += ['?'] * (string.ascii_uppercase.index(end_col) - string.ascii_uppercase.index(start_col) - 3)
        else:
            row += results
        # Add reddit account overview and redditmetis account overview links
        row.append(f"{constants.REDDIT_URL}user/{username}")
        row.append(user_url)
        row.append("FALSE")
        # Update the appropriate row with the info
        # Need to do idx + 1 because google sheets are 1-indexed while python is 0-indexed
        # raw=False allows us to do =HYPERLINK which we used for Most Downvoted, etc.
        #sheet_tab.update(f'{start_col}{idx + 1}:{end_col}{idx + 1}', [results], raw=False)
        #data_tab.append_row(row, value_input_option='USER_ENTERED')
        data_tab.update(f'A{data_tab_row_idx}:{end_col}{data_tab_row_idx}', [row], raw=False)
        data_tab_row_idx += 1


if __name__ == '__main__':
    main()
