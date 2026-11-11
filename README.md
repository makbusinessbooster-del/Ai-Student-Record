# AI Student Record Manager

A beginner-friendly Flask web application for managing student marks, calculating results, and generating AI-powered performance feedback and study tips with the Groq API.

## Features

- Add, view, search, update, and delete student records.
- Automatically calculate total marks, average percentage, and grade.
- Save records in `students.json` so they remain after restarting.
- Ask Groq AI to analyze performance and create personalized study tips.
- Validate marks (0–100), duplicate IDs, duplicate subjects, and missing fields.
- Responsive green-and-white interface.
- Student name and ID are never sent to the AI API.

## Technologies

Python 3, Flask, JSON, Groq Python SDK, python-dotenv, HTML, CSS, and JavaScript.

## Folder structure

```text
AI_Student_Record_Manager_Web/
├── app.py
├── ai_helper.py
├── students.json
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── templates/
│   └── index.html
└── README.md
```

## Setup on Windows

1. Install Python 3 and Visual Studio Code.
2. Open this project folder in VS Code.
3. Open the VS Code terminal: **Terminal > New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv venv
   ```

5. Activate it in PowerShell:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

   If you use Command Prompt instead, run `venv\Scripts\activate.bat`.

6. Install the packages:

   ```powershell
   py -m pip install -r requirements.txt
   ```

## Configure Groq

1. Create or sign in to your account at https://console.groq.com/.
2. Create an API key at https://console.groq.com/keys.
3. Open `.env` in VS Code.
4. Replace `your_actual_groq_api_key` with your own key.
5. Keep the key private. Never upload `.env` to GitHub. The `.gitignore` file excludes it.
6. `GROQ_MODEL` is set to `openai/gpt-oss-120b`. If Groq no longer makes that model available to your account, replace it with a supported text-generation model from your Groq console.

## Run the application

In the VS Code terminal, from the project folder:

```powershell
py app.py
```

The app opens in your browser at http://127.0.0.1:5000. Keep the terminal open while using it. Press `Ctrl+C` in the terminal to stop the server.

## How to use

1. Enter a unique Student ID, student name, class/semester, comma-separated subject names, and matching comma-separated marks.
2. Select **Add Student** to save the record.
3. Select a row in the table to load its details into the form.
4. Change the details and choose **Update Student** to save changes. The Student ID stays unchanged.
5. Select **Delete Student** to remove a record after confirming.
6. Search by student name or ID, or choose **Show All**.
7. Select a student, then choose **Analyze Performance** or **Generate Study Tips**. Wait while Groq generates the response.

## Result calculation

Each subject is marked out of 100. Average percentage is total marks divided by the number of subjects.

- A: 85% or above
- B: 70% to below 85%
- C: 60% to below 70%
- D: 50% to below 60%
- F: below 50%

For example, 88 + 76 + 92 + 81 = 337; 337 / 4 = 84.25%; grade B.

## Common problems

- **PowerShell says scripts are disabled:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate the environment again.
- **ModuleNotFoundError:** Activate `venv`, then run `py -m pip install -r requirements.txt`.
- **Missing API key:** Check that `.env` exists and `GROQ_API_KEY` contains your key. Restart `py app.py` after changing `.env`.
- **401 error:** The API key is invalid or revoked. Create a new key and update `.env`.
- **404/model not found:** Set `GROQ_MODEL` to a model currently available to your Groq account.
- **429/rate limit:** Wait and try again; check your Groq account limits.
- **Port already in use:** Close the other Flask process or stop it with `Ctrl+C`.

## GitHub safety

Before pushing to GitHub, confirm `.env` is not staged or committed. Upload `.env.example` instead. If an API key is accidentally published, revoke it immediately and create a new one.
