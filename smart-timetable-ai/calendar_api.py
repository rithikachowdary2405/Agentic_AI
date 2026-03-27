from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def connect_calendar():

    try:
        creds = Credentials.from_authorized_user_file("token.json")
        service = build("calendar", "v3", credentials=creds)
        return service
    except:
        return None


def get_events(service):

    if service is None:
        return []

    try:
        events_result = service.events().list(
            calendarId="primary",
            maxResults=20,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        return events

    except:
        return []


def create_event(service, title, start, end):

    if service is None:
        return

    event = {
        "summary": title,
        "start": {
            "dateTime": start,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Asia/Kolkata"
        },
    }

    service.events().insert(
        calendarId="primary",
        body=event
    ).execute()