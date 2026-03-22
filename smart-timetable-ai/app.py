import streamlit as st
import pandas as pd
from calendar_api import connect_calendar, create_event, get_events
from scheduler import check_conflict, find_free_time
from datetime import datetime, timedelta
from reminder import send_email_reminder
import re
import holidays

st.title("Smart Timetable Assistant")

service = connect_calendar()

# -----------------------
# FLEXIBLE TIME PARSER
# -----------------------
def parse_time_input(time_str):
    time_str = time_str.strip().lower()
    time_str = time_str.replace(".", "")
    time_str = time_str.replace(" ", "")

    if time_str.isdigit():
        hour = int(time_str)
        return datetime.strptime(f"{hour}:00", "%H:%M").time()

    time_str = re.sub(r'(\d)(am|pm)', r'\1 \2', time_str)

    formats = [
        "%H:%M",
        "%I:%M %p",
        "%I %p",
        "%I%p",
        "%H"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except:
            continue

    raise ValueError("Invalid time format")

# -----------------------
# SEMESTER
# -----------------------
semester = st.selectbox("Select Semester", ["Sem 1", "Sem 2"])

# -----------------------
# USER EMAIL
# -----------------------
user_email = st.text_input("Enter your email for reminders")

# -----------------------
# CREATE EVENT
# -----------------------
st.header("Create Event")

title = st.text_input("Event Title")

event_type = st.selectbox(
    "Event Type",
    ["Lecture", "Lab", "Tutorial", "Exam", "Personal"]
)

start_date = st.date_input("Start Date")
start_time_text = st.text_input("Start Time (e.g. 9, 9am, 2:30pm)", "09:00")

end_date = st.date_input("End Date")
end_time_text = st.text_input("End Time (e.g. 10, 10am, 3pm)", "10:00")

is_exam = st.checkbox("Is this an Exam?")

events = get_events(service)

current_year = datetime.now().year
india_holidays = holidays.India(years=[current_year])

if st.button("Add Event"):

    # -------- FIXED TRY BLOCK --------
    try:
        start_time = parse_time_input(start_time_text)
        end_time = parse_time_input(end_time_text)

        start_dt = datetime.combine(start_date, start_time)
        end_dt = datetime.combine(end_date, end_time)

    except ValueError:
        st.error("Enter time like 9, 9am, 2:30pm, or 14:30")
        st.stop()

    # -------- NORMAL FLOW --------
    if start_dt.date() in india_holidays:
        st.error("Cannot schedule on Indian holiday!")
        st.stop()

    if end_dt <= start_dt:
        st.error("End time must be after start time")

    else:
        start = start_dt.isoformat()
        end = end_dt.isoformat()

        full_title = f"{event_type} - {title}"

        conflict = check_conflict(events, start, end)

        if conflict:
            st.error("Time Conflict Detected!")

        else:
            create_event(service, full_title, start, end)

            # auto study slot for exams
            if is_exam:
                study_start = start_dt - timedelta(days=1)

                create_event(
                    service,
                    f"Study for {title}",
                    study_start.isoformat(),
                    start_dt.isoformat()
                )

            if user_email:
                send_email_reminder(user_email, title)

            st.success("Event Created Successfully")

# -----------------------
# UPCOMING EVENTS
# -----------------------
st.header("Upcoming Events")

events = get_events(service)

data = []
for event in events:
    data.append({
        "Title": event.get("summary", "No Title"),
        "Start": event["start"].get("dateTime")
    })

df = pd.DataFrame(data)
st.dataframe(df)

# -----------------------
# SEMESTER TEMPLATE
# -----------------------
st.header("Class Timetable (Semester Template)")

templates = pd.read_csv("semester_templates.csv")
filtered = templates[templates["Semester"] == semester]

st.dataframe(filtered)

if st.button("Load Semester Schedule to Calendar"):

    for _, row in filtered.iterrows():

        today = datetime.now()
        hour, minute = map(int, row["Time"].split(":"))

        start = today.replace(hour=hour, minute=minute, second=0)
        end = start + timedelta(hours=1)

        create_event(
            service,
            f"{row['Type']} - {row['Subject']}",
            start.isoformat(),
            end.isoformat()
        )

    st.success("Semester schedule added to calendar")

# -----------------------
# ASSIGNMENTS
# -----------------------
st.header("Assignments")

assignments = pd.read_csv("assignments.csv")

for _, row in assignments.iterrows():
    if row["Priority"] == "High":
        st.warning(f"High Priority: {row['Title']}")

st.dataframe(assignments)

# -----------------------
# INDIAN ACADEMIC CALENDAR
# -----------------------
st.header("Indian Academic Calendar")

today = datetime.now().date()

upcoming = []
for date, name in india_holidays.items():
    if date >= today:
        upcoming.append({"Date": date, "Event": name})

df_holidays = pd.DataFrame(upcoming[:10])
st.dataframe(df_holidays)

# -----------------------
# AI ASSISTANT
# -----------------------
st.header("AI Scheduling Assistant")

query = st.text_input("Ask: schedule meeting tomorrow at 5pm")

if query:

    query = query.lower()

    if "free" in query:

        free_slots = find_free_time(events)

        if free_slots:
            for slot in free_slots:
                st.write("Free from", slot[0], "to", slot[1])
        else:
            st.write("No free slots")

    elif "schedule" in query:

        tomorrow = datetime.now() + timedelta(days=1)

        match = re.search(r'(\d+)(am|pm)', query)

        if match:
            hour = int(match.group(1))
            if match.group(2) == "pm" and hour != 12:
                hour += 12
        else:
            hour = 17

        start_time = tomorrow.replace(hour=hour, minute=0, second=0)
        end_time = tomorrow.replace(hour=hour+1, minute=0, second=0)

        create_event(service, "AI Event", start_time.isoformat(), end_time.isoformat())

        if user_email:
            send_email_reminder(user_email, "AI Event")

        st.success(f"Event scheduled at {hour}:00")

    elif "assignment" in query:
        st.dataframe(assignments)

    else:
        st.write("Didn't understand")