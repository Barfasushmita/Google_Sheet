import os
import base64
from django.http import JsonResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.shortcuts import render

# Paths and constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials', 'token.json')
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1CrYexLUTGyIStFdVUzrdJ8tKOFjcC56JuW4FCipxbB0"
RANGE_NAME = "Form responses 1!A1:T1000"

def save_credentials_from_env():
    """
    Save credentials.json from a base64-encoded environment variable, if set.
    """
    google_credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    if google_credentials_base64:
        os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
        with open(CREDENTIALS_PATH, 'w') as f:
            f.write(base64.b64decode(google_credentials_base64).decode('utf-8'))

def get_spreadsheet_data():
    """
    Fetch data from the Google Sheets API using credentials and a token.
    """
    # Ensure credentials.json exists (create from environment variable if necessary)
    save_credentials_from_env()

    credentials = None

    # Load credentials from token.json if it exists
    if os.path.exists(TOKEN_PATH):
        credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid credentials, create new ones using credentials.json
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError("The 'credentials.json' file is missing.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the token for future use
        with open(TOKEN_PATH, "w") as token:
            token.write(credentials.to_json())

    try:
        # Access the Google Sheets API
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        return result.get("values", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def fetch_data(request):
    """
    View to fetch data from the Google Sheet and return it as JSON.
    """
    data = get_spreadsheet_data()
    return JsonResponse(data, safe=False)

def index(request):
    """
    View to render the index page.
    """
    return render(request, 'index.html')
