from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os, sqlite3, uuid, subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
THUMB_FOLDER = "thumbnails"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        title TEXT,
        description TEXT,
        thumbnail TEXT,
        views INTEGER DEFAULT 0,
        user_id INTEGER
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        text TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- サムネ生成 ----------------
def create_thumbnail(video_path, thumb_path):
    subprocess.run([
        "ffmpeg",
        "-i", video_path,
        "-ss", "00:00:01",
        "-vframes", "1",
        thumb_path
    ])

# ---------------- ホーム ----------------
@app.route('/')
def index():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos ORDER BY id DESC")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

# ---------------- アップロード ----------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['video']
        title = request.form.get('title')
        desc = request.form.get('description')

        ext = file.filename.rsplit('.',1)[1]
        filename = f"{uuid.uuid4()}.{ext}"
        filename = secure_filename(filename)

        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # サムネ生成
        thumb = f"{uuid.uuid4()}.jpg"
        thumb_path = os.path.join(THUMB_FOLDER, thumb)
        create_thumbnail(path, thumb_path)

        conn = sqlite3.connect('videos.db')
        c = conn.cursor()
        c.execute("INSERT INTO videos (filename,title,description,thumbnail,user_id) VALUES (?,?,?,?,?)",
                  (filename, title, desc, thumb, session['user_id']))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('upload.html')

# ---------------- 動画 ----------------
@app.route('/watch/<int:id>', methods=['GET','POST'])
def watch(id):
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()

    # 再生数++
    c.execute("UPDATE videos SET views = views + 1 WHERE id=?", (id,))

    c.execute("SELECT * FROM videos WHERE id=?", (id,))
    video = c.fetchone()

    # コメント投稿
    if request.method == 'POST':
        text = request.form.get('comment')
        c.execute("INSERT INTO comments (video_id,text) VALUES (?,?)", (id,text))

    # コメント取得
    c.execute("SELECT * FROM comments WHERE video_id=?", (id,))
    comments = c.fetchall()

    # 関連動画
    c.execute("SELECT * FROM videos WHERE id != ? ORDER BY RANDOM() LIMIT 5", (id,))
    related = c.fetchall()

    conn.commit()
    conn.close()

    return render_template("watch.html", video=video, comments=comments, related=related)

# ---------------- ログイン ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        conn = sqlite3.connect('videos.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pw))
        u = c.fetchone()
        conn.close()

        if u:
            session['user_id'] = u[0]
            return redirect('/')

    return render_template('login.html')

# ---------------- 登録 ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        conn = sqlite3.connect('videos.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",(user,pw))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------- 配信 ----------------
@app.route('/uploads/<f>')
def video_file(f):
    return send_from_directory(UPLOAD_FOLDER, f)

@app.route('/thumb/<f>')
def thumb_file(f):
    return send_from_directory(THUMB_FOLDER, f)

if __name__ == "__main__":
    app.run(debug=True)