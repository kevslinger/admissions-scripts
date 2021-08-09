import sys
sys.path.append('.')
from utils import google_utils
import os

"""We have a google sheet where people can put in their birthdays. But it hasn't been updated in years and
    so the sheet is wildly outdated! This script requires the output of get_contributor_list, and then it prints
    out each user that's on our birthday list that isn't in the contributor list.
"""

def main():
    contributor_list = []
    with open(os.path.join('output_files', 'ravenclaw_contributors_08_06_21.txt')) as f:
        for line in f.readlines():
            contributor_list.append(line.replace('\n', '').lower())

    gspread_client = google_utils.create_gspread_client()
    birthday_sheet = gspread_client.open_by_key('1-1ZhGctRMozdWTM6W4jbGOW1bHaKvosMj7T1Ix6XwC8').sheet1
    for row in birthday_sheet.get_all_values():
        if row[1].replace('\\', '').strip().lower() not in contributor_list:
            print(f"{row[1].replace(chr(92), '')} not in contributor list")


if __name__ == '__main__':
    main()
