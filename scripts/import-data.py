"""
Imports data from the shared Google spreadsheets
"""

from __future__ import print_function
import pickle
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of events and student profiles spreadsheet.
EVENTS_SPREADSHEET_ID = '1rdp3ll9gMX18RMCpwOIKmUWhLAN266mgea4PbLsJMBA'
EVENTS_RANGE_NAME = 'A1:G50'

STUDENT_SPREADSHEET_ID = '1BoCYvSTdUe5KAu1PfiHCVZqxzutNmoLv3WPnna0aGk0'
STUDENT_RANGE_NAME = 'A1:AC200'

# Spreadsheet fields to filter out (for privacy, relevance) or rename
EVENTS_FIELD_RENAME = {}
EVENTS_FIELD_FILTER = []

STUDENT_FIELD_RENAME = {
    "please_provide_your_biography_or_statement_written_in_third_person_max_150_words": "biography",
    "preferred_name_as_you_would_like_it_displayed_in_exhibition_and_promotional_texts_": "preferred_name",
    "please_upload_the_image_you_would_like_included_on_the_website_max_file_size_is_10mb": "image_location",
    "name_of_photographer_if_applicable": "photographer_name",
    "year_the_work_was_created": "year",
    "url_for_your_student_portfolio_to_be_featured_on_the_graduation_exhibition_website": "portfolio_url",
    "format_of_your_student_portfolio": "portfolio_format",
    "tags_for_your_work_select_all_that_apply": "tags",
}
STUDENT_FIELD_FILTER = ["", "email_address" , "anu_u_number", "mobile_phone_number", ]


def get_spreadsheet_values(id, range, rename_fields={}):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=id,
                                range=range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return []
    else:
        idx = 0
        data = []
        header = []
        for row in values:
            if row and idx==0:
                # cleanup the Google spreadsheet header
                header_tmp = [re.sub("[^0-9a-zA-Z_]+", "", r.lower().strip().replace(' ','_')) for r in row]
                # Filter out the fields we want to hide
                header = [r if r not in rename_fields else rename_fields[r] for r in header_tmp]
            elif row and idx>0:
                data.append(zip(header, row))
            else:
                print(row)
            idx += 1
        return data     


def data_to_toml(data, filetype='toml', filter_fields=[]):
    """
    Takes a list of pairs and turns it into TOML format
    """
    content = ""
    for a,b in data:
        if a not in filter_fields:
            if filetype=="md":
                content += f"{a}: \"{b}\"\n"
            else:
                content += f"{a} = \"{b}\"\n"
    if filetype=="md":
        content = f"---\n{content}---\n\nDefault content"
    return content


def import_events(dest, filetype="toml"):
    """
    Import events and write data to disk
    """
    os.makedirs(dest, exist_ok=True)
    # Get the spreadsheet data as [(field, value), ...]
    data = get_spreadsheet_values(EVENTS_SPREADSHEET_ID, EVENTS_RANGE_NAME, rename_fields=EVENTS_FIELD_RENAME)
    for idx, d in enumerate(data):
        with open(os.path.join(dest, f"{idx:02}.{filetype}"), 'w') as f:
            f.write(data_to_toml(d, filetype=filetype, filter_fields=EVENTS_FIELD_FILTER))


def import_students(dest, filetype="md"):
    """
    Import students and write data to disk
    """
    os.makedirs(dest, exist_ok=True)
    # Get the spreadsheet data as [(field, value), ...]
    data = get_spreadsheet_values(STUDENT_SPREADSHEET_ID, STUDENT_RANGE_NAME, rename_fields=STUDENT_FIELD_RENAME)
    for idx, d in enumerate(data):
        with open(os.path.join(dest, f"student-{idx:03}.{filetype}"), 'w') as f:
            f.write(data_to_toml(d, filetype=filetype, filter_fields=STUDENT_FIELD_FILTER))


def main():
    """ 
    """
    import_events("/mnt/d/dev/websites/amplified-together/hugo/data/events")
    import_students("/mnt/d/dev/websites/amplified-together/hugo/content/student")


if __name__ == '__main__':
    main()