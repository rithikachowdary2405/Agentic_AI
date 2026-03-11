import streamlit as st
from calendar_api import connect_calendar, create_event, get_events

st.title("Smart Timetable Assistant")

service = connect_calendar()

st.header("Create Event")

title = st.text_input("Event Title")
start = st.text_input("Start Time (2026-03-10T10:00:00)")
end = st.text_input("End Time (2026-03-10T11:00:00)")

if st.button("Add Event"):
    create_event(service, title, start, end)
    st.success("Event Created")

st.header("Upcoming Events")

events = get_events(service)

for event in events:
    st.write(event['summary'], event['start'].get('dateTime'))