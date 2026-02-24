from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'moddbloom_3', 
    'database': 'moodbloom_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- AI & ANALYTICS LOGIC ---
def analyze_sentiment(content):
    content = content.lower()
    positive = ['happy', 'great', 'love', 'amazing', 'excited', 'good', 'blessed']
    negative = ['sad', 'bad', 'cry', 'hurt', 'lonely', 'terrible', 'depressed']
    stressed = ['stress', 'hard', 'tired', 'exam', 'deadline', 'busy', 'pressure']
    
    score = 3  # Default Neutral
    if any(word in content for word in positive): score = 5
    elif any(word in content for word in negative): score = 1
    elif any(word in content for word in stressed): score = 2
    return score

def get_quote_for_entry(content):
    content = content.lower()
    category = 'happy'
    if any(word in content for word in ['sad', 'down', 'cry']): category = 'sad'
    elif any(word in content for word in ['stress', 'hard', 'exam']): category = 'stressed'
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quotes WHERE category = %s ORDER BY RAND() LIMIT 1", (category,))
    quote = cursor.fetchone()
    conn.close()
    return quote

def calculate_mood_trend(entries):
    if len(entries) < 2: 
        return {"status": "Seeding", "slope": 0, "msg": "Insufficient data.", "consistency": "Write more."}
    
    # Linear Regression Logic
    X = np.array(range(len(entries))).reshape(-1, 1)
    y = np.array([e['mood_score'] for e in reversed(entries)])
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]
    
    status = "Blooming" if slope > 0.1 else "Cloudy" if slope < -0.1 else "Steady"
    return {"status": status, "slope": round(slope, 2), "msg": "Trend Verified.", "consistency": "Consistent."}

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch Chart Data
    cursor.execute("SELECT mood_score, entry_date FROM journal_entries ORDER BY entry_date ASC LIMIT 10")
    chart_data = cursor.fetchall()
    dates = [row['entry_date'].strftime("%b %d") for row in chart_data]
    scores = [row['mood_score'] for row in chart_data] 
    
    # 2. Fetch Entries for Table (No Delete Logic needed here, just fetching)
    cursor.execute("SELECT * FROM journal_entries ORDER BY entry_date DESC")
    entries = cursor.fetchall()
    
    # 3. Calculate AI Trend
    trend = calculate_mood_trend(entries)
    conn.close()
    
    return render_template('dashboard.html', entries=entries, trend=trend, dates=dates, scores=scores)

@app.route('/journal')
def journal():
    new_quote = request.args.get('quote_text')
    new_author = request.args.get('quote_author')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    count = cursor.fetchone()[0]
    conn.close()
    
    current_date = datetime.now().strftime("%b %d, %Y")
    page_num = str(count + 1).zfill(2)
    
    return render_template('journal.html', 
                           display_quote={'text': new_quote, 'author': new_author} if new_quote else None,
                           current_date=current_date,
                           page_number=page_num)

@app.route('/add', methods=['POST'])
def add_entry():
    content = request.form.get('content')
    if content:
        mood_score = analyze_sentiment(content)
        quote = get_quote_for_entry(content)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO journal_entries (content, mood_score, theme) VALUES (%s, %s, %s)", 
                       (content, mood_score, 'General'))
        conn.commit()
        conn.close()
        
        return redirect(url_for('journal', quote_text=quote['text'], quote_author=quote['author']))
    return redirect(url_for('journal'))

# DELETE ROUTE REMOVED COMPLETELY

if __name__ == '__main__':
    app.run(debug=True, port=5001)