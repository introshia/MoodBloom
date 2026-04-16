# 🌸 MoodBloom
**The modern almanac of a wandering mind.**

MoodBloom is a full-stack digital journaling application crafted to help users understand their emotional trends. By combining a chic, vintage interface with a heuristic sentiment engine, the application naturally categorizes entries and maps emotional journeys through the art of journaling.

*Developed by **Danna** for Programming Languages at **Universidad de Dagupan** (March 2026).*

---

## ✨ Major Updates (v1.5)
* **Secure Authentication:** Implementation of a robust user registration and login system using hashed passwords (via `Werkzeug`) for maximum security.
* **Private Almanac Lockers:** Individualized database sessions ensure users only ever see their own private entries, turning the database into a secure multi-user platform.
* **Immersive Cozy Aesthetic:** A high-fidelity aesthetic redesign featuring a cozy, interactive room environment (Sanctuary) with a desk view, premium dark-mode stitched binder journal, and elegant typography.
* **AI Sentiment Engine:** Real-time analysis of entry text to categorize moods and provide predictive "Emotional Cartography" using Linear Regression.
* **Security Protocols:** Full integration of environment variables (`.env`) to protect sensitive database credentials from public exposure.

## 🛠️ Tech Stack & Architecture

* **Frontend:** HTML5, CSS3, Bootstrap 5.3, FontAwesome 6, AOS (Animate on Scroll), Chart.js
* **Backend:** Python 3, Flask, Scikit-learn, NumPy
* **Database:** MySQL Community Server
* **Security:** Python-Dotenv, Werkzeug Security (Password Hashing)
* **Version Control:** Git & GitHub

---

## 🚀 Local Installation (For Grading)
*(Note: If you are downloading this project to test it, follow these steps to ensure the hidden vault is configured correctly.)*

```bash
# 1. Clone the repository
git clone [https://github.com/introshia/MoodBloom.git](https://github.com/introshia/MoodBloom.git)

# 2. Navigate into the directory
cd MoodBloom

# 3. Install the Python dependencies
pip3 install -r requirements.txt

# 4. Configure the Secret Vault (.env)
# Create a file named .env and add your password:
echo "DB_PASSWORD=your_mysql_password" > .env

# 5. Configure the Database
# Create a local MySQL database named 'moodbloom_db'
# The app will automatically use the password from your .env

# 6. Start the server
python3 app.py