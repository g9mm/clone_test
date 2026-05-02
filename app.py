from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 🔥 ここが重要（DB自動修正）
def init_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()

    # テーブル作成（最低限）
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT
        )
    ''')

    # 既存カラム確認
    c.execute("PRAGMA table_info(videos)")
    columns = [col[1] for col in c.fetchall()]

    # 足りないカラムを追加
    if 'title' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN title TEXT")

    if 'description' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN description TEXT")

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos ORDER BY id DESC")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        title = request.form.get('title')
        description = request.form.get('description')

        if file and allowed_file(file.filename):
            # ファイル名を安全に生成
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            filename = secure_filename(filename)

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = sqlite3.connect('videos.db')
            c = conn.cursor()
            c.execute(
                "INSERT INTO videos (filename, title, description) VALUES (?, ?, ?)",
                (filename, title, description)
            )
            conn.commit()
            conn.close()

            return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)