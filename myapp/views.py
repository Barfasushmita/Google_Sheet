import os
import base64
from django.http import JsonResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.shortcuts import render

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials', 'token.json')

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1CrYexLUTGyIStFdVUzrdJ8tKOFjcC56JuW4FCipxbB0"
RANGE_NAME = "Form responses 1!A1:T1000"


def decode_base64_to_file(encoded_str, file_path):
    """
    Decodes a base64 string and writes it to a file.
    """
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(encoded_str))


def get_spreadsheet_data():
    """
    Fetches data from the Google Sheets API by using credentials and token from environment variables.
    """
    google_credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    google_token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')

    # Check if the environment variables are set
    if google_credentials_base64 and google_token_base64:
        # Decode and save the credentials and token files
        if not os.path.exists(CREDENTIALS_PATH):
            decode_base64_to_file(google_credentials_base64, CREDENTIALS_PATH)

        if not os.path.exists(TOKEN_PATH):
            decode_base64_to_file(google_token_base64, TOKEN_PATH)

        credentials = None
        if os.path.exists(TOKEN_PATH):
            credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                credentials = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(credentials.to_json())

        try:
            # Build the service to interact with the Sheets API
            service = build("sheets", "v4", credentials=credentials)
            sheets = service.spreadsheets()
            result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()

            # Return the values retrieved from the sheet
            return result.get("values", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    return []


def fetch_data(request):
    """
    Handles the fetch data request and returns data as JSON response.
    """
    data = get_spreadsheet_data()
    return JsonResponse(data, safe=False)


def index(request):
    """
    Renders the index page.
    """
    return render(request, 'index.html')
