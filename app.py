from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# フォルダ作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 許可拡張子
ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# DB初期化＆自動マイグレーション
def init_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT
        )
    ''')

    # カラム確認
    c.execute("PRAGMA table_info(videos)")
    columns = [col[1] for col in c.fetchall()]

    if 'title' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN title TEXT")

    if 'description' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN description TEXT")

    conn.commit()
    conn.close()

init_db()

# 一覧ページ
@app.route('/')
def index():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos ORDER BY id DESC")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

# アップロード
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('video')
        title = request.form.get('title')
        description = request.form.get('description')

        if not file or file.filename == '':
            return "ファイルが選択されていません"

        if not allowed_file(file.filename):
            return "mp4ファイルのみアップロード可能です"

        # 安全なファイル名に変換
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{uuid.uuid4()}.{ext}")

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

# 動画配信
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 🎥 詳細ページ（YouTube風）
@app.route('/watch/<int:video_id>')
def watch(video_id):
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    video = c.fetchone()
    conn.close()

    if video is None:
        return "動画が見つかりません", 404

    return render_template('watch.html', video=video)

if __name__ == '__main__':
    app.run(debug=True)