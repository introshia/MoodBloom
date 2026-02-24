# 🌸 MoodBloom
**A whimsical, AI-driven sanctuary for your thoughts.**

MoodBloom is a full-stack digital journaling application crafted to help users understand their emotional trends. By combining a chic, distraction-free interface with a heuristic sentiment engine, the application naturally categorizes entries and maps emotional journeys over time.

*Developed by Danna for Programming Languages at Universidad de Dagupan.*

---

## ✨ Features
* **AI Sentiment Analysis:** A heuristic engine silently analyzes the emotional weight of your words.
* **Predictive Trends:** Maps your journaling journey to predict whether upcoming days will be cloudy or bright.
* **Immutable Archive:** Secure local MySQL database integration to ensure data integrity.
* **Chic UI/UX:** A digital notebook layout with smooth scroll animations.

## 🛠️ Tech Stack & Architecture
**Frontend:** HTML5, CSS3, Bootstrap 5.3, Google Fonts
**Backend:** Python 3, Flask
**Database:** MySQL Community Server
**Version Control:** Git & GitHub

---

## 🚀 Local Installation (For Grading)
*(Note: If you are downloading this project to test it, run these commands in your terminal to set it up.)*

1. **Clone the repository:**
   `git clone https://github.com/introshia/MoodBloom.git`

2. **Navigate into the directory:**
   `cd MoodBloom`

3. **Install the Python dependencies:**
   `pip install -r requirements.txt`

4. **Configure the Database:**
   * Create a local MySQL database named `moodbloom_db`.
   * Update the `app.py` file with your local MySQL credentials.

5. **Start the server:**
   `python app.py`