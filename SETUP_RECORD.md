# MoodBloom - Project Setup & Tech Stack Record
**Developer:** Danna
**Course:** Programming Languages (Universidad de Dagupan)

## 1. System Requirements & Global Tools
These are the core applications installed on the MacBook to make development and version control possible:
* **Homebrew:** The package manager for macOS (used to install other terminal tools).
* **Git:** Version control system used to track code changes.
* **GitHub CLI (`gh`):** Installed via Homebrew to securely authenticate the MacBook terminal with GitHub.com.
* **VS Code:** The primary code editor used for Python, HTML, and CSS.

## 2. Database Environment
* **MySQL Community Server (Version 8.4.8):** The local relational database used to store journal entries and user data.
* **Database Name:** `moodbloom_db`
* **User:** `root` (Local access)

## 3. Python Backend & Machine Learning
The core logic engine running the web server and analyzing the journal entries.
* **Python 3.x:** The primary programming language.
* **Virtual Environment (`venv`):** Used to keep the project dependencies isolated and clean.
* **Flask:** The Python web framework used to connect the backend logic to the frontend HTML pages.
* **MySQL Connector:** The Python library used to communicate with the local MySQL database.
* **Linear Regression & Sentiment Libraries:** The AI Logic Engine dependencies used to process the emotional weight of journal entries and predict trends.

## 4. Frontend Architecture (No installation required - via CDN)
The user interface was built using external libraries linked directly in the HTML files to keep the project lightweight:
* **Bootstrap 5.3:** For responsive layout, grid systems, and the navigation bar.
* **FontAwesome 6.4.0:** For the chic icons used in the features and digital notebook.
* **AOS (Animate On Scroll) 2.3.1:** For the smooth fade-up and zoom animations on the Welcome page.
* **Google Fonts:** * *Indie Flower* (for the whimsical branding and titles).
    * *Inter* (for clean, readable paragraph text).
    * *Playfair Display* (for elegant quotes).