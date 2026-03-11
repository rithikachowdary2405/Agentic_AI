import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def connect_calendar():

    creds = Credentials(
        token=st.secrets["google_token"]["token"],
        refresh_token=st.secrets["google_token"]["refresh_token"],
        token_uri=st.secrets["google_token"]["token_uri"],
        client_id=st.secrets["google_token"]["client_id"],
        client_secret=st.secrets["google_token"]["client_secret"],
        scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=creds)

    return service


def create_event(service, title, start_time, end_time):

    event = {
        'summary': title,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    return event


def get_events(service):

    events_result = service.events().list(
        calendarId='primary',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    return events