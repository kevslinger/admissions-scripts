from selenium import webdriver

import constants
import google_utils
import gspread
import get_redditmetis_stats
import time
import os
import string
import requests
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
    admissions_tab = sheet.worksheet(constants.ADMISSIONS_TAB_NAME)
    # Set the options for our chrome driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.binary_location = constants.GOOGLE_CHROME_PATH
    # Get the Chrome Driver
    #driver = webdriver.Chrome(executable_path=constants.CHROMEDRIVER_PATH,
    #                          options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    # Call the function to look through each of the new rows on the sheet
    start_col = "G"
    end_col = "W"
    update_sheet(driver, admissions_tab, start_col, end_col)


def update_sheet(driver: webdriver, sheet_tab: gspread.Worksheet, start_col: str, end_col: str):
    # Loop through each row in the sheet from the back (we only care about new entries)
    for idx, row in reversed(list(enumerate(sheet_tab.get_all_values()))):
        # Check to see if the TIMESTAMP or USERNAME columns are empty.
        # TODO: is this the best way to check?
        if row[0] == "" or row[1] == "":
            continue
        # Both Timestamp and username are empty, check if the python columns are empty as well
        # TODO: This is kinda hacky
        # If two rows are full, we've already processed it, so we're done.
        elif row[6] != "" and row[7] != "":
            break
        # At this point, we have a timestamp and username, but have not processed the entry
        username = row[1]
        # Get the URL to open up with chrome
        user_url = f"{constants.REDDITMETIS_URL}{username}"
        driver.get(user_url)
        # Wait 5 seconds for the page to load TODO: different time?
        time.sleep(5)
        # Pulls in all the info we need about the reddit user
        results = get_redditmetis_stats.get_stats(driver)
        # This fails mechanism will on average let us speed up how long it takes for each person
        # If the page hasn't finished loading, we wait 10 seconds, then 15 seconds, then 30 seconds.
        # If the page still hasn't loaded by then (50 total seconds), we'll assume there was some error
        fails = 3

        comment_karma = -1
        while not results and fails > 0:
            print(f"Failed! {fails} fails remaining")
            results = get_redditmetis_stats.get_stats(driver)
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
                        comment_karma = -1
        # Could not get results after waiting for so long. Assume user causes an error on redditmetis
        # TODO: Maybe we should wait even longer? Just slows down the code though.
        if not results:
            print(f"User {row[1]} cannot be found on {constants.REDDITMETIS_URL}{username}!")
            # If we found their comment karma on the ABOUT page, then put it on the results list
            if comment_karma >= 0:
                results = [comment_karma]
            else:
                # Otherwise, we know nothing about them.
                results = ['?']
            # Add filler to the sheet
            # TODO: We do -2 because we then add the reddit and redditmetis links
            results += ['?'] * (string.ascii_uppercase.index(end_col) - string.ascii_uppercase.index(start_col) - 2)
        # Add reddit account overview and redditmetis account overview links
        results.append(f"{constants.REDDIT_URL}user/{username}")
        results.append(user_url)
        # Update the appropriate row with the info
        # Need to do idx + 1 because google sheets are 1-indexed while python is 0-indexed
        # raw=False allows us to do =HYPERLINK which we used for Most Downvoted, etc.
        sheet_tab.update(f'{start_col}{idx + 1}:{end_col}{idx + 1}', [results], raw=False)


if __name__ == '__main__':
    main()
