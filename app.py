from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# DB初期化（カラム追加版）
def init_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            title TEXT,
            description TEXT
        )
    ''')
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            conn = sqlite3.connect('videos.db')
            c = conn.cursor()
            c.execute(
                "INSERT INTO videos (filename, title, description) VALUES (?, ?, ?)",
                (file.filename, title, description)
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