from flask import Flask, render_template, Response, request, redirect, session
from deepface import DeepFace
import cv2
import mysql.connector

app = Flask(__name__)

app.secret_key = "moodai_secret"

# =========================
# MYSQL CONNECTION
# =========================

conn = mysql.connector.connect(

    host="127.0.0.1",

    port=3306,

    user="root",

    password="Shourya@123",

    database="moodai"
)

cursor = conn.cursor()

# =========================
# GLOBALS
# =========================

camera = None

current_mood = "Waiting"

confidence = 0

emoji = "😎"

last_songs = []
settings_data = {
    "dark_theme": True,
    "ambient_glow": True,
    "notifications": False,
    "live_overlay": True,
    "mirror_feed": True,
    "spotify_auto": True,
    "history_logs": True,
    "two_factor": False
}

# =========================
# SONGS
# =========================

def get_spotify_songs(mood):

    if mood == "happy":

        return [

            {
                "name":"Kesariya",
                "artist":"Arijit Singh",
                "embed":"https://open.spotify.com/embed/track/6VBhH7CyP56BXjp8VsDFPZ"
            },

            {
                "name":"Ilahi",
                "artist":"Arijit Singh",
                "embed":"https://open.spotify.com/embed/track/41kbTq3U5sYxMboLK8nIT1"
            },

            {
                "name":"Love You Zindagi",
                "artist":"Jasleen Royal",
                "embed":"https://open.spotify.com/embed/track/0AMhK4wsxmTQ1ySnwe7xYp"
            },

            {
                "name":"Badtameez Dil",
                "artist":"Benny Dayal",
                "embed":"https://open.spotify.com/embed/track/1gPkGM6qo3pgnjYHZJuVXB"
            }

        ]

    elif mood == "sad":

        return [

            {
                "name":"Channa Mereya",
                "artist":"Arijit Singh",
                "embed":"https://open.spotify.com/embed/track/1yYM2z8i7aYFt2KqDsvNQh"
            },

            {
                "name":"Agar Tum Saath Ho",
                "artist":"Alka Yagnik",
                "embed":"https://open.spotify.com/embed/track/4cXlAm4YQFENnM5r0DiWjo"
            },

            {
                "name":"Kabira",
                "artist":"Tochi Raina",
                "embed":"https://open.spotify.com/embed/track/2j9XxBWoxQOx0oQTTw9V7b"
            },

            {
                "name":"Tum Hi Ho",
                "artist":"Arijit Singh",
                "embed":"https://open.spotify.com/embed/track/56zZ48jdyY2oDXHVnwg5Di"
            }

        ]

    elif mood == "angry":

        return [

            {
                "name":"Kun Faya Kun",
                "artist":"A.R. Rahman",
                "embed":"https://open.spotify.com/embed/track/4wM1zC2wQe7h7n1r1rW7qF"
            },

            {
                "name":"Weightless",
                "artist":"Marconi Union",
                "embed":"https://open.spotify.com/embed/track/7pKfPomDEeI4TPT6EOYjn9"
            },

            {
                "name":"Iktara",
                "artist":"Kavita Seth",
                "embed":"https://open.spotify.com/embed/track/1A1o0U6pANBRZWgQ4E7Wm4"
            },

            {
                "name":"Safarnama",
                "artist":"Lucky Ali",
                "embed":"https://open.spotify.com/embed/track/5HNCy40Ni5BZJFw1TKzRsC"
            }

        ]

    else:

        return [

            {
                "name":"Perfect",
                "artist":"Ed Sheeran",
                "embed":"https://open.spotify.com/embed/track/0tgVpDi06FyKpA1z0VMD4v"
            },

            {
                "name":"Believer",
                "artist":"Imagine Dragons",
                "embed":"https://open.spotify.com/embed/track/0pqnGHJpmpxLKifKRmU6WP"
            },

            {
                "name":"Shape of You",
                "artist":"Ed Sheeran",
                "embed":"https://open.spotify.com/embed/track/7qiZfU4dY1lWllzX7mPBI3"
            },

            {
                "name":"Blinding Lights",
                "artist":"The Weeknd",
                "embed":"https://open.spotify.com/embed/track/0VjIjW4GlUZAMYd2vXMi3b"
            }

        ]

# =========================
# HOME
# =========================

@app.route('/')

def home():

    if 'user' not in session:

        return redirect('/login')

    return render_template(
        'index.html',
        username=session['user']
    )

# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET','POST'])

def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        cursor.execute(

            "INSERT INTO users(username,password) VALUES(%s,%s)",

            (username,password)
        )

        conn.commit()

        return redirect('/login')

    return render_template('register.html')

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET','POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        cursor.execute(

            "SELECT * FROM users WHERE username=%s AND password=%s",

            (username,password)
        )

        user = cursor.fetchone()

        if user:

            session['user'] = username

            return redirect('/')

        else:

            return render_template(

                'login.html',

                error="Invalid Username or Password ❌"
            )

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')

def logout():

    session.pop('user',None)

    return redirect('/login')

# =========================
# START CAMERA
# =========================

@app.route('/start_camera')

def start_camera():

    global camera

    if camera is None:

        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)

        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

    return "started"

# =========================
# STOP CAMERA
# =========================

@app.route('/stop_camera')

def stop_camera():

    global camera

    if camera is not None:

        camera.release()

        camera = None

    return "stopped"

# =========================
# VIDEO FEED
# =========================

@app.route('/video')

def video():

    def generate_frames():

        global camera

        while True:

            if camera is None:

                break

            success, frame = camera.read()

            if not success:

                continue

            # MIRROR EFFECT
            frame = cv2.flip(frame,1)

            ret, buffer = cv2.imencode('.jpg', frame)

            frame = buffer.tobytes()

            yield (

                b'--frame\r\n'

                b'Content-Type: image/jpeg\r\n\r\n'

                + frame +

                b'\r\n'
            )

    return Response(

        generate_frames(),

        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =========================
# CAMERA PAGE
# =========================

@app.route('/camera')

def camera_page():

    fetch = cv2.VideoCapture(0)

    fetch.release()

    return render_template('camera.html')

# =========================
# DETECT MOOD
# =========================

@app.route('/detect')

def detect():

    global camera
    global current_mood
    global confidence
    global emoji
    global last_songs

    if 'user' not in session:

        return redirect('/login')

    if camera is None:

        return redirect('/camera')

    success, frame = camera.read()

    if not success:

        return "Camera Error"

    # MIRROR FRAME
    frame = cv2.flip(frame,1)

    # SAVE IMAGE
    cv2.imwrite("face.jpg", frame)

    try:

        result = DeepFace.analyze(

            img_path="face.jpg",

            actions=['emotion'],

            detector_backend='opencv',

            enforce_detection=False,

            silent=True
        )

        emotions = result[0]['emotion']

        current_mood = max(

            emotions,

            key=emotions.get
        )

        confidence = float(

            round(

                emotions[current_mood],

                2
            )
        )

    except:

        current_mood = "neutral"

        confidence = 70.0

    # EMOJIS

    if current_mood == "happy":

        emoji = "😊"

    elif current_mood == "sad":

        emoji = "😔"

    elif current_mood == "angry":

        emoji = "😡"

    elif current_mood == "surprise":

        emoji = "😲"

    else:

        emoji = "😎"

    songs = get_spotify_songs(current_mood)

    last_songs = songs

    # SAVE DATABASE

    cursor.execute(

        "INSERT INTO moods(username,mood,confidence) VALUES(%s,%s,%s)",

        (
            session['user'],
            current_mood,
            confidence
        )
    )

    conn.commit()

    return render_template(

        'result.html',

        mood=current_mood,

        confidence=confidence,

        emoji=emoji,

        songs=songs
    )

# =========================
# ANALYTICS
# =========================

@app.route('/analytics')

def analytics():

    if 'user' not in session:

        return redirect('/login')

    cursor.execute(

        "SELECT * FROM moods WHERE username=%s",

        (session['user'],)
    )

    history = cursor.fetchall()

    return render_template(

        'analytics.html',

        mood=current_mood,

        confidence=confidence,

        history=history
    )

# =========================
# SETTINGS
# =========================

@app.route('/settings', methods=['GET','POST'])
def settings():

    global settings_data

    if request.method == "POST":

        settings_data["dark_theme"] = "dark_theme" in request.form
        settings_data["ambient_glow"] = "ambient_glow" in request.form
        settings_data["notifications"] = "notifications" in request.form
        settings_data["live_overlay"] = "live_overlay" in request.form
        settings_data["mirror_feed"] = "mirror_feed" in request.form
        settings_data["spotify_auto"] = "spotify_auto" in request.form
        settings_data["history_logs"] = "history_logs" in request.form
        settings_data["two_factor"] = "two_factor" in request.form

    return render_template(
        "setting.html",
        settings=settings_data
    )

# =========================
# RECOMMENDATIONS
# =========================

@app.route('/recommendations')

def recommendations():

    return render_template(

        'recommendation.html',

        songs=last_songs
    )

# =========================
# RUN
# =========================

if __name__ == '__main__':

    app.run(debug=True)