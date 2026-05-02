from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# DB初期化
def init_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ホーム（動画一覧）
@app.route('/')
def index():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

# アップロード画面
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            conn = sqlite3.connect('videos.db')
            c = conn.cursor()
            c.execute("INSERT INTO videos (filename) VALUES (?)", (file.filename,))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))

    return render_template('upload.html')

# 動画配信
@app.route('/video/<filename>')
def video(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))

if __name__ == '__main__':
    app.run(debug=True)