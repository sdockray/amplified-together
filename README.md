# Amplified Together

Hugo website for the 2020 ANU School of Art and Design graduating students along with a Python script that pulls data from some Google spreadsheets for the content to build the site,

## Setup Hugo

You should be able to just go into the `hugo/` directory and test, build, etc.

I usually do this while I am developing:

```
hugo serve --templateMetrics --disableFastRender --renderToDisk --ignoreCache
```

We will figure out how to deploy some time later. My guess is that we will either just build locally and rsync the hugo directory to the webserver; **or** we will set up the Python script and install hugo on the server and set up a way to trigger a build on demand.


## Setup Python script

If you need to set up the Python script so that it can pull data from the Google Spreadsheets, do the following. It will write events and student data to the `hugo/` directory.

0. In `scripts/`, setup a virtual environment with Python 3.6+

1. Get `credentials.json` and put into `scripts/`

See [https://developers.google.com/sheets/api/quickstart/python](https://developers.google.com/sheets/api/quickstart/python)

2. Install Python dependencies:

`pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

3. From scripts directory, do:

`python import-data.py`