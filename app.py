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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
# Initialize VADER sentiment analyzer globally
analyzer = SentimentIntensityAnalyzer()
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
    """
    Uses the VADER (Valence Aware Dictionary and sEntiment Reasoner) library
    to analyze the entire entry for context, intensity, and negations.
    """
    if not content:
        return {"score": 3, "pillar": "peace", "reflection": "What is one truth you've been avoiding today?"}

    # Get sentiment scores from VADER
    vs = analyzer.polarity_scores(content)
    compound = vs['compound'] # Ranges from -1.0 to 1.0
    
    # Map compound score to 1-5 scale
    if compound >= 0.6: final_score = 5       # Happy
    elif compound >= 0.1: final_score = 4     # Calm
    elif compound > -0.1: final_score = 3     # Neutral
    elif compound > -0.6: final_score = 2     # Sad
    else: final_score = 1                     # Stressed

    # Pillar Detection (keywords are still good for categorizing 'topics')
    text = content.lower()
    pillar = "Peace"
    if any(w in text for w in ['work', 'time', 'manage', 'schedule', 'todo', 'busy', 'deadline']): pillar = "Balance"
    elif any(w in text for w in ['learn', 'new', 'goal', 'better', 'future', 'skill', 'try', 'growth']): pillar = "Growth"
    elif any(w in text for w in ['health', 'body', 'eat', 'sleep', 'energy', 'feeling', 'wellness']): pillar = "Wellness"
    elif any(w in text for w in ['quiet', 'still', 'calm', 'nature', 'breathe', 'meditate', 'peace']): pillar = "Peace"

    # Dynamic Reflection Logic
    questions = {
        "Balance": "Is it the quantity of tasks—or the weight of expectations—that truly feels out of balance today?",
        "Growth": "What part of this 'new' self are you most afraid to leave behind as you grow?",
        "Wellness": "If your body could speak without using words right now, what's the first thing it would ask for?",
        "Peace": "In the middle of this quiet moment, what's the one noise you're still trying to ignore?"
    }
    
    reflection = questions.get(pillar, "What is one truth you've been avoiding today?")
    if final_score >= 4: reflection = "This vibrancy feels real—how can you preserve a piece of this light for a darker day?"
    elif final_score <= 2: reflection = "When the weight feels this heavy, what is the smallest possible kindness you can show yourself?"

    return {
        "score": final_score,
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
        return {"score": score, "mood": "high", "label": "Happy", "color": "#5BB8F5", "light": "#98D3F5", "dark": "#2A88BF", "mouth": "M3 3 Q11 12 19 3"}
    elif score >= 60:
        return {"score": score, "mood": "balanced", "label": "Calm", "color": "#6DBF8A", "light": "#9DDBB0", "dark": "#3A8A56", "mouth": "M3 6 Q11 2 19 6"}
    elif score >= 40:
        return {"score": score, "mood": "neutral", "label": "Neutral", "color": "#F5C842", "light": "#FAE092", "dark": "#BF9210", "mouth": "M4 5 L18 5"}
    elif score >= 20:
        return {"score": score, "mood": "low", "label": "Sad", "color": "#E87FA0", "light": "#FFAAC4", "dark": "#B54A6E", "mouth": "M3 3 Q11 9 19 3"}
    else:
        return {"score": score, "mood": "drained", "label": "Stressed", "color": "#A99BC4", "light": "#C4B5E8", "dark": "#7E6BA9", "mouth": "M5 3 Q11 3 17 3"}

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
    if 'user_id' in session:
        return redirect(url_for('archive'))
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

    # 1b. Fetch user's custom collections
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    user_collections = cursor.fetchall()
    conn.close()

    # 2. Process entries
    now = datetime.now()
    current_month_str = now.strftime("%B %Y")
    shelves_data = {}

    color_map = {
        5: 'c-sage', 4: 'c-slate', 3: 'c-ochre', 2: 'c-terr', 1: 'c-rose', 'default': 'c-dust'
    }

    arts = ['botanical', 'linen', 'face', 'wood', 'clouds']
    bgs = ["#C8D898", "#EDE4D2", "#A8C4E4", "#DDBEAA", "#F0EAD6"]
    elastics = ["#1a2810", "#222222", "#283858", "#604818", "#1A1A1A"]
    featured_journals = []

    # Map collection_id -> collection name for quick lookup
    collection_map = {c['id']: c for c in user_collections}

    mood_label_map = {5: 'Happy', 4: 'Calm', 3: 'Neutral', 2: 'Sad', 1: 'Stressed'}

    for i, entry in enumerate(all_entries):
        display_text = get_preview_text(entry['content'])
        entry['display_text'] = (display_text[:60] + '...') if len(display_text) > 60 else display_text
        entry['color_class'] = color_map.get(entry['mood_score'], color_map['default'])
        entry['formatted_date'] = entry['entry_date'].strftime("%b %d")
        entry['mood_label'] = mood_label_map.get(entry['mood_score'], 'Steady')
        entry['month_label'] = entry['entry_date'].strftime("%B %Y")

        # Monthly shelves fallback (for Jinja no-JS)
        if not entry.get('collection_id'):
            month_year = entry['month_label']
            if month_year not in shelves_data:
                shelves_data[month_year] = []
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

    # Build JSON-serialisable snapshots for the client-side view switcher
    all_entries_json = [{
        'id': e['id'],
        'color_class': e['color_class'],
        'formatted_date': e['formatted_date'],
        'mood_score': e['mood_score'],
        'mood_label': e['mood_label'],
        'month_label': e['month_label'],
        'collection_id': e.get('collection_id'),
    } for e in all_entries]

    user_collections_json = [
        {'id': c['id'], 'name': c['name'], 'cover_color': c['cover_color']}
        for c in user_collections
    ]

    # 3. Organize Monthly Shelves (uncollected entries only)
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

    # 4. Enrich collections with their entry count
    for col in user_collections:
        col['entry_count'] = sum(1 for e in all_entries if e.get('collection_id') == col['id'])

    # 5. AI Mood Trend (Linear Regression)
    trend = calculate_mood_trend(all_entries)
    
    # 6. Chart Data
    chart_points = []
    config_map = {
        5: {"c": "#5BB8F5", "label": "Happy"},
        4: {"c": "#6DBF8A", "label": "Calm"},
        3: {"c": "#F5C842", "label": "Neutral"},
        2: {"c": "#E87FA0", "label": "Sad"},
        1: {"c": "#A99BC4", "label": "Stressed"}
    }
    for i, e in enumerate(reversed(all_entries[:15])):
        d_str = e['entry_date'].strftime("%b %d")
        score = e['mood_score']
        chart_points.append({
            "label": d_str,
            "val": score,
            "color": config_map.get(score, config_map[3])["c"],
            "mood": config_map.get(score, config_map[3])["label"]
        })
    
    chart_labels = [p["label"] for p in chart_points]
    chart_scores = [p["val"] for p in chart_points]
    chart_colors = [p["color"] for p in chart_points]
    chart_moods = [p["mood"] for p in chart_points]

    # Greeting & Stats
    hour = now.hour
    greeting_prefix = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    raw_username = session.get('username', 'Alex')
    clean_username = raw_username.replace('_', ' ').title()
    greeting = f"{greeting_prefix}, {clean_username}."
    stats_msg = f"You've inscribed {len(all_entries)} memories in your Archive this year."

    # 7. Atmosphere Companion (Energy Widget)
    latest_text = get_preview_text(all_entries[0]['content']) if all_entries else ""
    companion_data = calculate_energy_data(latest_text)

    return render_template('pages/archive.html',
                          shelves=ordered_shelves,
                          user_collections=user_collections,
                          all_entries_json=all_entries_json,
                          user_collections_json=user_collections_json,
                          featured_journals=featured_journals,
                          greeting=greeting,
                          stats_msg=stats_msg,
                          trend=trend,
                          chart_labels=chart_labels,
                          chart_scores=chart_scores,
                          chart_colors=chart_colors,
                          chart_moods=chart_moods,
                          companion=companion_data)


# ── COLLECTION API ROUTES ──────────────────────────────────────────────────────

@app.route('/collections', methods=['GET'])
def list_collections():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    collections = cursor.fetchall()
    conn.close()
    # Convert datetimes to strings for JSON
    for c in collections:
        if c.get('created_at'):
            c['created_at'] = c['created_at'].isoformat()
    return {'success': True, 'collections': collections}, 200


@app.route('/collections', methods=['POST'])
def create_collection():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        cover_color = data.get('cover_color', '#C8D898')
        art_style = data.get('art_style', 'linen')
        if not name:
            return {'success': False, 'message': 'A collection needs a name.'}, 400
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO collections (user_id, name, cover_color, art_style) VALUES (%s, %s, %s, %s)",
            (user_id, name, cover_color, art_style)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'success': True, 'id': new_id, 'name': name, 'cover_color': cover_color, 'art_style': art_style}, 201
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/collections/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Verify ownership before deleting
    cursor.execute("SELECT id FROM collections WHERE id = %s AND user_id = %s", (collection_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return {'success': False, 'message': 'Not found or unauthorized'}, 404
    # Un-assign entries (ON DELETE SET NULL handles this, but be explicit)
    cursor.execute("UPDATE journal_entries SET collection_id = NULL WHERE collection_id = %s", (collection_id,))
    cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
    conn.commit()
    conn.close()
    return {'success': True}, 200


@app.route('/collections/<int:collection_id>/assign', methods=['POST'])
def assign_entry_to_collection(collection_id):
    """Assign or re-assign an existing entry to a collection."""
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verify entry ownership
        cursor.execute("SELECT id FROM journal_entries WHERE id = %s AND user_id = %s", (entry_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Entry not found'}, 404
        cursor.execute("UPDATE journal_entries SET collection_id = %s WHERE id = %s", (collection_id, entry_id))
        conn.commit()
        conn.close()
        return {'success': True}, 200
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@app.route('/writing')
def writing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('sanctuary', open='journal'))



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

    cursor.execute("SELECT username, joined_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM journal_entries WHERE user_id = %s", (user_id,))
    total_entries = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1) as words FROM journal_entries WHERE user_id = %s", (user_id,))
    word_row = cursor.fetchone()
    total_words = int(word_row['words']) if word_row and word_row['words'] else 0

    # Top mood: map mood_score int to a label
    cursor.execute("SELECT mood_score, COUNT(*) as cnt FROM journal_entries WHERE user_id = %s AND mood_score IS NOT NULL GROUP BY mood_score ORDER BY cnt DESC LIMIT 1", (user_id,))
    mood_row = cursor.fetchone()
    mood_labels = {1: 'Stressed', 2: 'Sad', 3: 'Neutral', 4: 'Calm', 5: 'Happy'}
    top_mood = mood_labels.get(mood_row['mood_score'], 'Steady') if mood_row else 'None yet'

    cursor.execute("SELECT DISTINCT DATE(entry_date) as d FROM journal_entries WHERE user_id = %s ORDER BY d DESC", (user_id,))
    days = [row['d'] for row in cursor.fetchall()]
    streak = 0
    if days:
        from datetime import date, timedelta
        check = date.today()
        for d in days:
            if d == check or d == check - timedelta(days=1):
                streak += 1
                check = d
            else:
                break

    conn.close()
    joined = user['joined_at'].strftime("%B %Y") if user.get('joined_at') else "April 2026"
    return render_template('pages/profile.html', user=user, stats=total_entries, joined=joined, total_words=total_words, top_mood=top_mood, streak=streak)

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
        
        # Optional: assign to a collection on save
        collection_id = data.get('collection_id', None)

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO journal_entries (content, mood_score, theme, user_id, collection_id) VALUES (%s, %s, %s, %s, %s)",
            (content, mood_score, 'Default', user_id, collection_id)
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