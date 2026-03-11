import streamlit as st
import pandas as pd
from calendar_api import connect_calendar, create_event, get_events
from scheduler import check_conflict, find_free_time
from datetime import datetime,time

st.title("Smart Timetable Assistant")

service = connect_calendar()

st.header("Create Event")

title = st.text_input("Event Title")

start_date = st.date_input("Start Date")
start_time = st.time_input("Start Time", value=time(9,0), step=60)

end_date = st.date_input("End Date")
end_time = st.time_input("End Time", value=time(10,0), step=60)

start = datetime.combine(start_date, start_time).isoformat()
end = datetime.combine(end_date, end_time).isoformat()

events = get_events(service)

if st.button("Add Event"):

    conflict = check_conflict(events, start, end)

    if conflict:
        st.error("Time Conflict Detected!")
    else:
        create_event(service, title, start, end)
        st.success("Event Created")

st.header("Upcoming Events")

events = get_events(service)

data = []

for event in events:
    data.append({
        "Title": event["summary"],
        "Start": event["start"].get("dateTime")
    })

df = pd.DataFrame(data)

st.dataframe(df)

st.header("Class Timetable")

timetable = pd.read_csv("smart-timetable-ai/timetable.csv")

st.dataframe(timetable)

st.header("Assignments")

assignments = pd.read_csv("assignments.csv")

st.dataframe(assignments)

st.header("Scheduling Assistant")

query = st.text_input("Ask something like: find free time")

if "free" in query.lower():

    free_slots = find_free_time(events)

    for slot in free_slots:
        st.write("Free from", slot[0], "to", slot[1])