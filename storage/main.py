from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024 * 1024 # 16 MB max (nope)

PASSWORD = "Sciences123*"

def password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get('authenticated') != 'true':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            response = redirect(url_for('index'))
            response.set_cookie('authenticated', 'true')
            return response
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)

@app.route('/')
@app.route('/<path:subfolder>')
@password_required
def index(subfolder=''):
    current_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    if not os.path.exists(current_path):
        abort(404)
    files = os.listdir(current_path)
    files_and_folders = []
    for f in files:
        full_path = os.path.join(current_path, f)
        is_folder = os.path.isdir(full_path)
        files_and_folders.append({'name': f, 'is_folder': is_folder})
    return render_template('index.html', files=files_and_folders, current_path=subfolder)

@app.route('/create_file', methods=['POST'])
@password_required
def create_file():
    filename = request.form['filename']
    subfolder = request.form['subfolder']
    open(os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename), 'a').close()
    return redirect(url_for('index', subfolder=subfolder))

@app.route('/create_folder', methods=['POST'])
@password_required
def create_folder():
    foldername = request.form['foldername']
    subfolder = request.form['subfolder']
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], subfolder, foldername), exist_ok=True)
    return redirect(url_for('index', subfolder=subfolder))

@app.route('/rename', methods=['POST'])
@password_required
def rename():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    subfolder = request.form['subfolder']
    os.rename(os.path.join(app.config['UPLOAD_FOLDER'], subfolder, old_name),
              os.path.join(app.config['UPLOAD_FOLDER'], subfolder, new_name))
    return redirect(url_for('index', subfolder=subfolder))

@app.route('/delete', methods=['POST'])
@password_required
def delete():
    filename = request.form['filename']
    subfolder = request.form['subfolder']
    path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)
    return redirect(url_for('index', subfolder=subfolder))

@app.route('/upload', methods=['POST'])
@password_required
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    subfolder = request.form['subfolder']
    if file.filename == '':
        return redirect(url_for('index', subfolder=subfolder))
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
        file.save(save_path)
    return redirect(url_for('index', subfolder=subfolder))

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.json.get('password')
    if password == PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)