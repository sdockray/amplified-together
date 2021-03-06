"""
Imports data from the shared Google spreadsheets
"""

from __future__ import print_function
import pickle
import os.path
import io
import re
import urllib
from pprint import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload 

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
    ]

# The ID and range of events and student profiles spreadsheet.
EVENTS_SPREADSHEET_ID = '1rdp3ll9gMX18RMCpwOIKmUWhLAN266mgea4PbLsJMBA'
EVENTS_RANGE_NAME = 'A1:G50'

STUDENT_SPREADSHEET_ID = '1lXAEVHKVwAKF0B9dIXVuuOO3_219o-2B-7HwvLHS4uI'
# STUDENT_SPREADSHEET_ID = '1BoCYvSTdUe5KAu1PfiHCVZqxzutNmoLv3WPnna0aGk0'
STUDENT_RANGE_NAME = 'A1:AC200'

# Spreadsheet fields to filter out (for privacy, relevance) or rename
EVENTS_FIELD_RENAME = {}
EVENTS_FIELD_FILTER = []
EVENTS_FIELD_TAXONOMIES = []

STUDENT_FIELD_RENAME = {
    "please_provide_your_biography_or_statement_written_in_third_person_max_150_words": "biography",
    "please_provide_your_artist_statement_max_150_words": "biography",
    "preferred_name_as_you_would_like_it_displayed_in_exhibition_and_promotional_texts": "preferred_name",
    "please_upload_the_image_you_would_like_included_on_the_website_max_file_size_is_10mb": "image_location",
    "name_of_photographer_if_applicable": "photographer_name",
    "year_the_work_was_created": "year",
    "url_for_your_student_portfolio_to_be_featured_on_the_graduation_exhibition_website": "portfolio_url",
    "format_of_your_student_portfolio": "portfolio_format",
    "tags_for_your_work_select_all_that_apply": "tags",
    "curatorial_themes": "themes",
    "discipline_area": "disciplines"
}
STUDENT_FIELD_FILTER = ["", "email_address" , "anu_u_number", "mobile_phone_number", ]
STUDENT_FIELD_TAXONOMIES = ["themes"]


def get_google_creds():
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
    return creds


def get_spreadsheet_values(id, range, rename_fields={}):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = get_google_creds()

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


def data_to_toml(data, filetype='toml', filter_fields=[], taxonomy_fields=[]):
    """
    Takes a list of pairs and turns it into TOML format
    """
    content = ""
    fields = {}
    for a,b in data:
        if a not in filter_fields:
            fields[a] = b
            if filetype=="md":
                if a in taxonomy_fields:
                    items = "\n".join([f"- {b1}" for b1 in b.split(", ")])
                    content += f"{a}:\n{items}\n"
                else:
                    b = b.replace('"', '\\"').strip()
                    content += f"{a}: \"{b}\"\n"
            else:
                if a in taxonomy_fields:
                    items = ", ".join([f"\"{b1}\"" for b1 in b.split(", ")])
                    content += f"{a} = [{items}]\n"
                else:
                    content += f"{a} = \"{b}\"\n"
    if filetype=="md":
        content = f"---\n{content}---\n\nDefault content"
    return content, fields


def data_to_filename(d, filetype, base_dir=False, append=0):
    """
    Generate a unique, urlized filename
    """
    fn = False
    fn = d.setdefault("first_name", "").strip()
    ln = d.setdefault("last_name", "").strip()
    pn = d.setdefault("preferred_name", fn).strip()
    fn = f"{pn}" if pn.endswith(ln) else f"{pn}-{ln}" 
    #fn = f'{d.setdefault("first_name", "")}-{d.setdefault("last_name", "")}' if not d['preferred_name'] else f'{d.setdefault("preferred_name", "")}-{d.setdefault("last_name", "")}'
    if append and append>0:
        fn = f"{fn}-{append}"
    fn = f"{fn}.{filetype}"
    fn = urllib.parse.quote(fn.replace(" ", "-").lower(), safe="")
    letter = d["last_name"][0:1].lower()
    os.makedirs(os.path.join(base_dir, letter), exist_ok=True)
    with open(os.path.join(base_dir, letter, "_index.md"), 'w') as f:
        f.write(f'---\ntitle: "{letter.upper()}"\n---\n')
    """
    # Need to figure out how to overwrite with new data, while alos preserving uniqueness
    if base_dir and os.path.exists(os.path.join(base_dir, letter, fn)):
        append += 1
        return data_to_filename(data, filetype, base_dir=base_dir, append=append)
    """
    return os.path.join(letter, fn), fn


def import_events(dest, filetype="toml"):
    """
    Import events and write data to disk
    """
    os.makedirs(dest, exist_ok=True)
    # Get the spreadsheet data as [(field, value), ...]
    data = get_spreadsheet_values(EVENTS_SPREADSHEET_ID, EVENTS_RANGE_NAME, rename_fields=EVENTS_FIELD_RENAME)
    for idx, d in enumerate(data):
        content, _ =data_to_toml(d, 
            filetype=filetype, 
            filter_fields=EVENTS_FIELD_FILTER, 
            taxonomy_fields=STUDENT_FIELD_TAXONOMIES)
        with open(os.path.join(dest, f"{idx:02}.{filetype}"), 'w') as f:
            f.write(content)


def import_students(dest, images_dest, filetype="md"):
    """
    Import students and write data to disk
    """
    # Prepare for downlaoding images
    creds = get_google_creds()
    drive = build('drive', 'v3', credentials=creds)
    # Now process student data
    os.makedirs(dest, exist_ok=True)
    # Get the spreadsheet data as [(field, value), ...]
    data = get_spreadsheet_values(STUDENT_SPREADSHEET_ID, STUDENT_RANGE_NAME, rename_fields=STUDENT_FIELD_RENAME)
    for idx, d in enumerate(data):
        content, fields = data_to_toml(d, 
            filetype=filetype, 
            filter_fields=STUDENT_FIELD_FILTER, 
            taxonomy_fields=STUDENT_FIELD_TAXONOMIES)
        filename, slug = data_to_filename(fields, filetype, base_dir=dest)
        if filename:
            print("Writing:", filename)
            with open(os.path.join(dest, filename), 'w') as f:
                f.write(content)
        # write image
        download_image(fields['image_location'], drive, slug, images_dest)


def download_image(url, drive, slug, dest):
    #filename = "test.jpg"
    #urllib.request.urlretrieve(url,filename) 
    file_dest = os.path.join(dest, f"{slug}.jpg")
    if not os.path.exists(file_dest):
        parts = url.split('=')
        if len(parts)==2:
            file_id = parts[1]
            # data = drive.files().get(fileId=file_id, fields='*').execute()
            # pprint(data)
            request = drive.files().get_media(fileId=file_id)
            fh = io.FileIO(file_dest, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))



def main():
    """ 
    """
    import_events("/mnt/d/dev/websites/amplified-together/hugo/data/events")
    import_students("/mnt/d/dev/websites/amplified-together/hugo/content/student", "/mnt/d/dev/websites/amplified-together/hugo/static/images")
    # creds = get_google_creds()
    # drive = build('drive', 'v3', credentials=creds)
    # download_image("https://drive.google.com/open?id=13i0ae2dgs_HHJpJ_0KshCYONqvj7-YKu", drive, '.')
    
if __name__ == '__main__':
    main()