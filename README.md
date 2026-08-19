# FlaskTalk

A simple messenger built with Flask. Register, log in, see all users, and chat with real-time updates.

## Features

- Register and log in with username and password
- List of all registered users in the sidebar
- Private messaging between users
- Auto-updating chats (messages every 2 seconds, user list every 3 seconds)
- Data stored in SQLite

## Tech Stack

- Python 3
- Flask
- SQLite (built-in, no setup required)
- HTML, CSS, JavaScript (no frameworks)

## Installation

```
pip install flask
```

## Run

```
python app.py
```

The app will be available at:

```
http://localhost:5000
```

On first run, the database file `flasktalk.db` is created automatically.

## Project Structure

```
FlaskTalk/
├── app.py                 server and all the logic
├── flasktalk.db            database (created automatically)
├── templates/
│   ├── login.html          login page
│   ├── register.html       registration page
│   └── chat.html           main chat interface
└── static/
    └── style.css            styles
```

## How to Use

1. Open `http://localhost:5000`
2. Register an account
3. Open the app in a second tab (or another device) and register a second account
4. Select a contact in the sidebar and start chatting

## Notes

- This project uses Flask's built-in server and is intended for local use or learning purposes
