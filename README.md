HealthBot
A powerful web application that allows users to search for recipes and health tips with keyword and fuzzy matching, user authentication, and caching for lightning-fast results.
Supports both Flask (frontend + search) and FastAPI (backend APIs).

✨ Features
🔍 Search Recipes & Health Tips with keyword & fuzzy matching

👤 User Registration & Login

⚡ Caching-enabled Search for faster results

📜 Search History for registered users

🕒 Guest Search with Daily Limit

🎨 Beautiful UI with sidebar history display

🛠 Requirements
Flask

FastAPI

python-Levenshtein

Flask_SQLAlchemy

PyMySQL

fuzzywuzzy

📦 Installation
1️⃣ Create and activate virtual environment
bash
Copy
Edit
python -m venv venv
venv\Scripts\activate    # For Windows
source venv/bin/activate # For macOS/Linux

2️⃣ Install dependencies
bash
Copy
Edit
pip install Flask SQLAlchemy mysql-connector-python Werkzeug
pip install fastapi uvicorn
pip install flask fuzzywuzzy python-Levenshtein PyMySQL

3️⃣ Run the applications
Run Flask app
bash
Copy
Edit
python app.py
Copy the link shown in the terminal and paste it into your browser.

Run FastAPI app
bash
Copy
Edit
uvicorn main:app --reload
Access via: http://127.0.0.1:8000

🖥 Tech Stack
Python 3.10+

Flask

FastAPI

SQLAlchemy (ORM)

MySQL (or SQLite for development)

HTML/CSS

Jinja2 Templates

FuzzyWuzzy (fuzzy search)

📌 Notes
Make sure MySQL server is running before starting the app.

You can change database credentials in the configuration file.

Guest users have a daily search limit.

If you want, I can now add a “How It Works” diagram and GitHub-style badges so this README looks like a polished open-source project.
That would make it stand out more in portfolios.
