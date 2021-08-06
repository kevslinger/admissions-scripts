

from utils import google_utils
import os

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
