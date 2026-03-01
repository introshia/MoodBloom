# MoodBloom - Project Setup & Tech Stack Record
**Developer:** Danna
**Course:** Programming Languages (Universidad de Dagupan)

## 1. System Requirements & Global Tools
These are the core applications installed on the MacBook to make development and version control possible:
* **Homebrew:** The package manager for macOS used to install terminal-based development tools.
* **Git:** Version control system used to track code changes and manage project history.
* **GitHub CLI (gh):** A command-line tool used to securely authenticate the MacBook terminal with GitHub.com.
* **VS Code:** The primary Integrated Development Environment (IDE) used for writing Python, HTML, and CSS.

## 2. Database & Security Environment
* **MySQL Community Server (Version 8.4.8):** The local relational database used to store journal entries and user accounts.
* **Secret Management (.env):** Implementation of `python-dotenv` to isolate sensitive database credentials from the source code.
* **Database Name:** `moodbloom_db`
* **Tables:** Includes `users` (storing hashed credentials) and `journal_entries` (storing content linked to specific user IDs).

## 3. Python Backend & Machine Learning
The core logic engine running the web server and performing data analysis.
* **Python 3.x:** The primary programming language used for backend development.
* **Virtual Environment (venv):** A dedicated environment used to keep project-specific dependencies isolated from the global system.
* **Flask:** The lightweight web framework used to route requests and connect the backend to the UI.
* **Werkzeug Security:** A library utilized for secure password hashing and authentication verification.
* **MySQL Connector:** The bridge library that allows Python to execute SQL commands within the local database.
* **AI Logic Engine:** Powered by **Scikit-learn (Linear Regression)** and **NumPy** to calculate emotional scores and predict mood trends.

## 4. Frontend Architecture (via CDN)
The user interface was built using external libraries to ensure a responsive and aesthetically pleasing experience:
* **Bootstrap 5.3:** For the responsive layout, grid system, and the frosted-glass navigation bar.
* **FontAwesome 6.4.0:** For the vintage-inspired icons used throughout the almanac features.
* **AOS (Animate On Scroll) 2.3.1:** For the smooth, sophisticated fade-up animations on the landing page.
* **Chart.js:** A JavaScript library used to render the "Emotional Cartography" mood trend graph on the dashboard.
* **Google Fonts:**
    * *Pinyon Script*: For the primary branding and elegant almanac-style headings.
    * *Inter*: For clean, modern, and readable body text.