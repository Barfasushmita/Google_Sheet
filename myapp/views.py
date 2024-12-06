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
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'client_secret.json')  # Use your OAuth Client ID file
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials', 'token.json')
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1CrYexLUTGyIStFdVUzrdJ8tKOFjcC56JuW4FCipxbB0"
RANGE_NAME = "Form responses 1!A1:T1000"

def save_credentials_from_env():
    """
    Save the OAuth Client ID JSON file from an environment variable, if provided.
    """
    client_secret_base64 = os.getenv('GOOGLE_CLIENT_SECRET_BASE64')
    if client_secret_base64:
        os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
        with open(CREDENTIALS_PATH, 'w') as f:
            f.write(base64.b64decode(client_secret_base64).decode('utf-8'))

def get_spreadsheet_data():
    """
    Fetch data from Google Sheets using OAuth Client ID for authentication.
    """
    # Save the client_secret.json if provided as an environment variable
    save_credentials_from_env()

    credentials = None

    # Check if token.json exists and load credentials
    if os.path.exists(TOKEN_PATH):
        credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If credentials are missing or invalid, perform the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError("The 'client_secret.json' file is missing.")

            # Use InstalledAppFlow to authenticate with the OAuth Client ID
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

            # For headless environments, use run_console()
            print("No browser detected. Running in console mode. Follow the instructions to authenticate.")
            credentials = flow.run_console()

        # Save the token for future use
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(credentials.to_json())

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
    Django view to fetch data from the Google Sheet and return as JSON.
    """
    data = get_spreadsheet_data()
    return JsonResponse(data, safe=False)

def index(request):
    """
    Django view to render the index page.
    """
    return render(request, 'index.html')
