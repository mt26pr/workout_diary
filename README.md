# WorkoutDiary - Full-Stack Fitness Tracker

A stylish, responsive, and secure full-stack web application designed to log and analyze your daily workouts. Built with Python (Flask) on the backend and an interactive custom dashboard on the frontend, this app focuses on smooth user experience, clean data validation, and visual consistency.

---

##  Features

### 🔒 Authentication & Security
- **Secure Access:** Session-based authentication implemented via `Flask-Login`.
- **Data Protection:** Passwords are fully hashed and salted using `Werkzeug` before entering the database.
- **Protected Routes:** Unauthorized users are automatically redirected to the login screen.

### 📝 Core Functionality (CRUD)
- **Log Activity:** Add a new workout by selecting the sport type from a dynamic relational database list.
- **Smart Duration Inputs:** Custom numeric inputs with **quick-select presets** (15m, 30m, 45m, 1h) optimized for both desktop and mobile tapping.
- **Native Date Pickers:** Forms utilize HTML5 calendar drop-downs with dark-mode compliance to guarantee zero input errors and clean database formats (`YYYY-MM-DD`).
- **History Management:** View, edit, or safely delete your workout logs with reactive Flask flash alerts confirming successful actions.

### 📊 Advanced Analytics Dashboard
- **Top Metrics Cards:** Visually clean grid blocks tracking **Total Sessions**, **Total Hours Spent** (automatically converted from minutes with smart rounding), and your **Favorite Activity** based on database volume.
- **Interactive Timelines:** Beautiful, fluid line charts generated via **Chart.js** displaying workout consistency over a 7-day (Week) or 30-day (Month) rolling period.
- **GitHub-Style Contribution Grid:** Toggle the "Year" view to unlock a pixel-perfect activity heatmap grid spanning the last 365 days. Cubes dynamically shift shades of green based on training intensity per day, complete with precise hover tooltips.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask, Flask-Login, Werkzeug
- **Database:** SQLite (Normalized relational schema with foreign key constraints mapping Users ➔ Workouts ➔ Sports)
- **Frontend:** Semantic HTML5, CSS3 Custom Properties (Modern Slate Dark Theme, CSS Flexbox & Grid architectures)
- **Charts & Visuals:** Chart.js (Interactive data fetching via Jinja2 JSON serialization)

---
## ⚙️ Installation & Setup

Follow these quick steps to launch the application locally:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/workout-diary.git](https://github.com/YOUR_USERNAME/workout-diary.git)
   cd workout-diary
   
2. **Initialize the database:**
   Run the database setup script to generate tables and populate default sports:
   ```bash 
   python setup_db.py

3. **Run the Flask application:**
      ```bash 
      python app.py
4. **Open in browser:**

Navigate to http://127.0.0.1:5000/ and register a new account to start crushing your goals!
## Project Structure

```text
workout-diary/
│
├── static/
│   └── style.css            # Unified global stylesheets & typography
│
├── templates/
│   ├── login.html           # Auth screens
│   ├── register.html
│   ├── dashboard.html       # Hub page
│   ├── index.html          # Workout history
│   ├── add.html             # Contextual entry forms
│   ├── edit.html
│   └── analytics.html       # ChartJS & Heatmap grid hub
│
├── app.py                   # Main Flask backend controller & SQL statements
├── setup_db.py              # Database initialization & sport seeds script
├── .gitignore               # Keeps internal .db and cache files out of production
└── README.md                # Project documentation