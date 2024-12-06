import os
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

def get_spreadsheet_data():
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
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        return result.get("values", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def fetch_data(request):
    data = get_spreadsheet_data()
    return JsonResponse(data, safe=False)


def index(request):
    return render(request, 'index.html')
