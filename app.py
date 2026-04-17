import os
from dotenv import load_dotenv

# Load the hidden variables from your .env file
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import numpy as np
from datetime import datetime, timedelta
import io
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.debug = True

# This keeps the user's login session secure!
app.secret_key = 'super_secret_moodbloom_key'

# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'), 
    'database': 'moodbloom_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- AI & ANALYTICS LOGIC ---
def analyze_sentiment(content):
    c = content.lower()
    
    # Mood Mapping
    positive = ['happy', 'great', 'love', 'amazing', 'excited', 'good', 'blessed', 'proud', 'wonderful', 'joy']
    negative = ['sad', 'bad', 'cry', 'hurt', 'lonely', 'terrible', 'depressed', 'grief', 'heavy', 'miserable']
    stressed = ['stress', 'hard', 'tired', 'exam', 'deadline', 'busy', 'pressure', 'overwhelmed', 'anxious']
    
    score = 3
    if any(w in c for w in positive): score = 5
    elif any(w in c for w in negative): score = 1
    elif any(w in c for w in stressed): score = 2
    
    # Pillar Detection
    pillar = "Peace" # Default
    if any(w in c for w in ['work', 'time', 'manage', 'schedule', 'todo', 'busy', 'juggling', 'deadline']): pillar = "Balance"
    elif any(w in c for w in ['learn', 'new', 'goal', 'better', 'future', 'skill', 'try', 'growth', 'evolve']): pillar = "Growth"
    elif any(w in c for w in ['health', 'body', 'eat', 'sleep', 'energy', 'feeling', 'wellness', 'yoga', 'medicine']): pillar = "Wellness"
    elif any(w in c for w in ['quiet', 'still', 'calm', 'nature', 'breathe', 'meditate', 'peace', 'serene']): pillar = "Peace"

    # Reflective Question Generator
    questions = {
        "Balance": "Is it the quantity of tasks—or the weight of expectations—that truly feels out of balance today?",
        "Growth": "What part of this 'new' self are you most afraid to leave behind as you grow?",
        "Wellness": "If your body could speak without using words right now, what's the first thing it would ask for?",
        "Peace": "In the middle of this quiet moment, what's the one noise you're still trying to ignore?"
    }
    
    # Dynamic nuance for reflection
    reflection = questions.get(pillar, "What is one truth you've been avoiding that this entry is trying to tell you?")
    if score >= 4: reflection = f"This vibrancy feels real—how can you preserve a piece of this light for a darker day?"
    elif score <= 2: reflection = f"When the weight feels this heavy, what is the smallest possible kindness you can show yourself?"

    return {
        "score": score,
        "pillar": pillar.lower(),
        "reflection": reflection
    }

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
        return {"status": "Seeding", "slope": 0, "msg": "The pages are fresh.", "consistency": "Write your first entry."}
    
    # Linear Regression Logic
    X = np.array(range(len(entries))).reshape(-1, 1)
    y = np.array([e['mood_score'] for e in reversed(entries)])
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]
    
    status = "Blooming" if slope > 0.1 else "Cloudy" if slope < -0.1 else "Steady"
    return {"status": status, "slope": round(slope, 2), "msg": "Trend Verified.", "consistency": "Consistent."}
def calculate_energy_data(content):
    if not content:
        return {"score": 50, "mood": "neutral", "label": "Resting", "color": "#F5C842"}
    
    c = content.lower()
    # Basic Energy Analysis (Keywords + Length)
    high = ['excited', 'amazing', 'great', 'love', 'happy', 'bloom', 'wonderful', 'active']
    low = ['tired', 'exhausted', 'sad', 'bad', 'lonely', 'drain', 'heavy', 'storm']
    
    score = 50
    if any(word in c for word in high): score += 30
    if any(word in c for word in low): score -= 30
    
    # Emotional Nuance
    if len(c) > 200: score += 10 # Long reflections = higher energy
    score = max(0, min(100, score))
    
    if score >= 80: 
        return {"score": score, "mood": "energized", "label": "Vibrant", "color": "#5BB8F5", "light": "#8DD4FF", "dark": "#2E7FC4", "mouth": "M2 7 Q11 1 20 7"}
    elif score >= 60: 
        return {"score": score, "mood": "balanced", "label": "Serene", "color": "#6DBF8A", "light": "#9DDBB0", "dark": "#3A8A56", "mouth": "M3 6 Q11 2 19 6"}
    elif score >= 40: 
        return {"score": score, "mood": "neutral", "label": "Steady", "color": "#F5C842", "light": "#FFE07A", "dark": "#C49010", "mouth": "M4 5 Q11 5 18 5"}
    elif score >= 20: 
        return {"score": score, "mood": "low", "label": "Muted", "color": "#E87FA0", "light": "#FFAAC4", "dark": "#B54A6E", "mouth": "M3 3 Q11 9 19 3"}
    else: 
        return {"score": score, "mood": "drained", "label": "Heavy", "color": "#A99BC4", "light": "#C4B5E8", "dark": "#7E6BA9", "mouth": "M5 3 Q11 3 17 3"}

def calculate_streak(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT DATE(entry_date) as entry_date 
        FROM journal_entries 
        WHERE user_id = %s 
        ORDER BY entry_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 0
        
    today = datetime.now().date()
    last_entry_date = rows[0]['entry_date']
    
    if last_entry_date < (today - timedelta(days=1)):
        return 0
    
    streak = 1
    current_date = last_entry_date
    for row in rows[1:]:
        if row['entry_date'] == (current_date - timedelta(days=1)):
            streak += 1
            current_date = row['entry_date']
        else:
            break
            
    return streak

def get_preview_text(content):
    if not content: return ""
    
    # Check if content is JSON (typical for Sanctuary canvas saves)
    if content.strip().startswith('{') and content.strip().endswith('}'):
        import json
        try:
            data = json.loads(content)
            if 'text' in data:
                return data['text'].strip().replace('\n', ' ')
        except:
            pass
            
    return content.strip().replace('\n', ' ')



# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return f"Error: Username might already be taken. Try another!"

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password_attempt):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('sanctuary')) 
        else:
            return "Invalid username or password. Please try again."

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))


# --- MAIN APP ROUTES ---

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/sanctuary')
def sanctuary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    streak = calculate_streak(user_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT content FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 30", (user_id,))
    recent_entries = cursor.fetchall()
    conn.close()
    
    processed_entries = []
    for e in recent_entries:
        text = get_preview_text(e['content'])
        processed_entries.append({"text": text, "location": "", "cats": [], "fav": False})
        
    processed_entries.reverse()
    return render_template('pages/sanctuary.html', streak_days=streak, recent_entries=processed_entries)

@app.route('/archive')
def archive():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch ALL entries for shelves
    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC", (user_id,))
    all_entries = cursor.fetchall()
    conn.close()

    # 2. Process for traditional monthly shelves
    now = datetime.now()
    current_month_str = now.strftime("%B %Y")
    shelves_data = {} 

    color_map = {
        5: 'c-sage', 4: 'c-slate', 3: 'c-ochre', 2: 'c-terr', 1: 'c-rose', 'default': 'c-dust'
    }

    # Mood-to-Art mapping for the 3D Shelf
    art_map = {
        5: 'botanical', 4: 'clouds', 3: 'linen', 2: 'face', 1: 'wood', 'default': 'linen'
    }

    arts = ['botanical', 'linen', 'face', 'wood', 'clouds']
    bgs = ["#C8D898", "#EDE4D2", "#A8C4E4", "#DDBEAA", "#F0EAD6"]
    elastics = ["#1a2810", "#222222", "#283858", "#604818", "#1A1A1A"]
    featured_journals = []


    for i, entry in enumerate(all_entries):
        month_year = entry['entry_date'].strftime("%B %Y")
        if month_year not in shelves_data: shelves_data[month_year] = []
        
        display_text = get_preview_text(entry['content'])
        entry['display_text'] = (display_text[:60] + '...') if len(display_text) > 60 else display_text
        entry['color_class'] = color_map.get(entry['mood_score'], color_map['default'])
        entry['formatted_date'] = entry['entry_date'].strftime("%b %d")
        
        shelves_data[month_year].append(entry)

        # Prepare first 5 for the 3D Featured Shelf with variety
        if i < 5:
            featured_journals.append({
                "id": entry['id'],
                "title": entry['formatted_date'],
                "pages": entry['theme'] if (entry['theme'] and entry['theme'] != 'Default') else "Personal Chronicle",
                "elastic": elastics[i % len(elastics)],
                "bg": bgs[i % len(bgs)],
                "art": arts[i % len(arts)],
                "content_preview": entry['display_text']
            })


    # 3. Organize Monthly Shelves
    ordered_shelves = []
    if current_month_str in shelves_data:
        entries = shelves_data[current_month_str]
        ordered_shelves.append({
            "label": "Currently Writing",
            "featured": entries[:3],
            "archive_count": max(0, len(entries) - 3)
        })
        del shelves_data[current_month_str]
    else:
        ordered_shelves.append({"label": "Currently Writing", "featured": [], "archive_count": 0})

    sorted_months = sorted(shelves_data.keys(), key=lambda x: datetime.strptime(x, "%B %Y"), reverse=True)
    for month in sorted_months:
        entries = shelves_data[month]
        ordered_shelves.append({
            "label": month,
            "featured": entries[:3],
            "archive_count": max(0, len(entries) - 3)
        })

    # 4. AI Mood Trend (Linear Regression)
    trend = calculate_mood_trend(all_entries)
    
    # 5. Chart Data
    chart_data_map = {}
    config_map = {
        5: {"c": "#5BB8F5", "label": "Radiant"},
        4: {"c": "#6DBF8A", "label": "Serene"},
        3: {"c": "#F5C842", "label": "Muted"},
        2: {"c": "#E87FA0", "label": "Pensive"},
        1: {"c": "#A99BC4", "label": "Heavy"}
    }
    for e in reversed(all_entries[:15]): 
        d_str = e['entry_date'].strftime("%b %d")
        score = e['mood_score']
        chart_data_map[d_str] = {
            "val": score, 
            "color": config_map.get(score, config_map[3])["c"],
            "label": config_map.get(score, config_map[3])["label"]
        }
    
    chart_labels = list(chart_data_map.keys())
    chart_scores = [v["val"] for v in chart_data_map.values()]
    chart_colors = [v["color"] for v in chart_data_map.values()]
    chart_moods = [v["label"] for v in chart_data_map.values()]

    # Greeting & Stats
    hour = now.hour
    greeting_prefix = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    greeting = f"{greeting_prefix}, {session.get('username', 'Alex')}."
    stats_msg = f"You've inscribed {len(all_entries)} memories in your Archive this year."

    # 6. Atmosphere Companion (Energy Widget)
    latest_text = get_preview_text(all_entries[0]['content']) if all_entries else ""
    companion_data = calculate_energy_data(latest_text)

    return render_template('pages/archive.html', 
                          shelves=ordered_shelves, 
                          featured_journals=featured_journals,
                          greeting=greeting, 
                          stats_msg=stats_msg,
                          trend=trend,
                          chart_labels=chart_labels,
                          chart_scores=chart_scores,
                          chart_colors=chart_colors,
                          chart_moods=chart_moods,
                          companion=companion_data)

@app.route('/writing')
def writing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('sanctuary', open='journal'))

# --- LEGACY REDIRECTS ---
@app.route('/dashboard')
def legacy_dashboard():
    return redirect(url_for('archive'))

@app.route('/cozy-room')
def legacy_cozy_room():
    return redirect(url_for('sanctuary'))

@app.route('/journal')
def legacy_journal():
    return redirect(url_for('writing'))


@app.route('/install')
def install():
    return render_template('pages/install.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch User Data
    cursor.execute("SELECT username, joined_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    # 2. Fetch Stats
    cursor.execute("SELECT COUNT(*) as total FROM journal_entries WHERE user_id = %s", (user_id,))
    stats = cursor.fetchone()
    
    conn.close()
    
    # Format 'Member Since'
    joined = user['joined_at'].strftime("%B %Y") if user.get('joined_at') else "April 2026"
    
    return render_template('pages/profile.html', user=user, stats=stats['total'], joined=joined)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if new_username:
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
            session['username'] = new_username
            
        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
            
        conn.commit()
        flash("Your curator identity has been successfully updated.")
    except Exception as e:
        flash(f"Error updating profile: {str(e)}")
    finally:
        conn.close()
        
    return redirect(url_for('profile'))

@app.route('/save_entry', methods=['POST'])
def save_entry():
    # SECURITY
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        mood_score_override = data.get('mood_score', None)
        
        if not content:
            return {'success': False, 'message': 'Content cannot be empty'}, 400
        
        user_id = session['user_id']
        
        # Analyze sentiment from content
        ai_result = analyze_sentiment(content)
        mood_score = ai_result['score']
        
        # Get a relevant quote (legacy support)
        quote = get_quote_for_entry(content)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO journal_entries (content, mood_score, theme, user_id) VALUES (%s, %s, %s, %s)",
            (content, mood_score, 'Default', user_id)
        )
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Entry saved successfully',
            'ai_analysis': ai_result,
            'quote': quote.get('text') if quote else None
        }, 200
        
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/add', methods=['POST'])
def add_entry():
    # SECURITY
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    content = request.form.get('content')
    mood_chip = request.form.get('mood') # Catches the selected chip from the new UI!
    
    if content:
        ai_result = analyze_sentiment(content)
        mood_score = ai_result['score']
        quote = get_quote_for_entry(content)
        user_id = session['user_id']
        
        # If they clicked a chip, save it as the theme. Otherwise, default to 'General'
        theme_to_save = mood_chip if mood_chip else 'General'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        # Save the new entry WITH the user's ID attached
        cursor.execute("INSERT INTO journal_entries (content, mood_score, theme, user_id) VALUES (%s, %s, %s, %s)", 
                       (content, mood_score, theme_to_save, user_id))
        conn.commit()
        conn.close()
        
        # Safely redirect with the quote
        if quote:
            return redirect(url_for('journal', quote_text=quote.get('text'), quote_author=quote.get('author')))
        else:
            return redirect(url_for('journal'))
            
    return redirect(url_for('journal'))

@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    
    if 'file' not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400
    
    if file:
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        user_id = session['user_id']
        file_data = file.read()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_media (user_id, filename, mimetype, media_data) VALUES (%s, %s, %s, %s)",
            (user_id, filename, mimetype, file_data)
        )
        media_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "url": f"/get_media/{media_id}",
            "type": "video" if filename.lower().endswith(('.mp4', '.webm', '.mov')) else "image"
        }

@app.route('/get_media/<int:media_id>')
def get_media(media_id):
    if 'user_id' not in session:
        return "Unauthorized", 401
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_media WHERE id = %s AND user_id = %s", (media_id, user_id))
    media = cursor.fetchone()
    conn.close()
    
    if media:
        return send_file(
            io.BytesIO(media['media_data']),
            mimetype=media['mimetype'],
            download_name=media['filename']
        )
    return "Not Found", 404

# --- PWA SERVICE WORKER ROUTE ---
@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js')


# --- ERROR HANDLERS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)