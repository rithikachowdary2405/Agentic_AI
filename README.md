# Smart Timetable Assistant

An AI-powered academic scheduling assistant that helps students manage classes, assignments, exams, and personal events using Google Calendar integration and Generative AI.

---

##  Features

###  Smart Calendar Management
- Google Calendar integration
- Monthly, weekly and daily calendar views
- Create and manage academic and personal events
- Export schedule as CSV

###  AI Scheduling Assistant
- View upcoming calendar events
- Find available free time slots
- Schedule meetings using natural language
- View assignment information
- Answer general academic queries using Google Gemini AI

### Conflict Detection
- Detects scheduling conflicts before creating events
- Prevents overlapping events
- Suggests available free slots

###  Assignment Tracker
- Displays assignment deadlines
- Highlights high-priority assignments
- Deadline notifications

###  Exam Planner
- Automatically creates study sessions before exams
- Prevents scheduling on Indian public holidays

###  Email Notifications
- Sends reminder emails for created events
- Sends assignment deadline reminders

### 🗓 Dashboard
- Upcoming events overview
- Upcoming Indian holidays
- Academic schedule summary

---

## Tech Stack

- Python
- Streamlit
- Google Calendar API
- Google Gemini API
- Pandas
- SQLite
- SMTP (Gmail)
- Streamlit Calendar
- Holidays (India)

---

## Project Structure

```
smart-timetable-ai/
│
├── app.py
├── ai_agent.py
├── calendar_api.py
├── scheduler.py
├── scheduler_jobs.py
├── reminder.py
├── llm_agent.py
├── database.py
├── assignments.csv
├── timetable.csv
├── semester_templates.csv
├── requirements.txt
├── user_data.db
├── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-timetable-ai.git

cd smart-timetable-ai
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

## Configuration

### Google Calendar API

1. Create a project in Google Cloud Console.
2. Enable Google Calendar API.
3. Download `credentials.json`.
4. Authenticate to generate `token.json`.

---

### Gemini API

Set your API key.

Example:

```python
GEMINI_API_KEY="YOUR_API_KEY"
```

---

### Gmail Reminder

Configure your Gmail App Password.

Example:

```
EMAIL_ADDRESS=your_email@gmail.com

EMAIL_PASSWORD=your_app_password
```

---

## AI Assistant Examples

You can ask:

```
What are my upcoming events?

Show my free slots

Schedule meeting tomorrow at 5pm

Show assignments

What is Generative AI?

Explain Cyber Security
```

---

## Screens

- Dashboard
- Create Event
- Calendar
- Assignment Tracker
- AI Scheduling Assistant

---
