from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify
import os
from werkzeug.utils import secure_filename

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = 'files'
application.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024 * 1024 # 16 MB max (nope)

@application.route('/')
@application.route('/<path:subfolder>')
def index(subfolder=''):
    current_path = os.path.join(application.config['UPLOAD_FOLDER'], subfolder)
    if not os.path.exists(current_path):
        abort(404)
    files = os.listdir(current_path)
    files_and_folders = []
    for f in files:
        full_path = os.path.join(current_path, f)
        is_folder = os.path.isdir(full_path)
        files_and_folders.append({'name': f, 'is_folder': is_folder})
    return render_template('index.html', files=files_and_folders, current_path=subfolder)

@application.route('/create_file', methods=['POST'])
def create_file():
    filename = request.form['filename']
    subfolder = request.form['subfolder']
    open(os.path.join(application.config['UPLOAD_FOLDER'], subfolder, filename), 'a').close()
    return redirect(url_for('index', subfolder=subfolder))

@application.route('/create_folder', methods=['POST'])
def create_folder():
    foldername = request.form['foldername']
    subfolder = request.form['subfolder']
    os.makedirs(os.path.join(application.config['UPLOAD_FOLDER'], subfolder, foldername), exist_ok=True)
    return redirect(url_for('index', subfolder=subfolder))

@application.route('/rename', methods=['POST'])
def rename():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    subfolder = request.form['subfolder']
    os.rename(os.path.join(application.config['UPLOAD_FOLDER'], subfolder, old_name),
              os.path.join(application.config['UPLOAD_FOLDER'], subfolder, new_name))
    return redirect(url_for('index', subfolder=subfolder))

@application.route('/delete', methods=['POST'])
def delete():
    filename = request.form['filename']
    subfolder = request.form['subfolder']
    path = os.path.join(application.config['UPLOAD_FOLDER'], subfolder, filename)
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)
    return redirect(url_for('index', subfolder=subfolder))

@application.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    subfolder = request.form['subfolder']
    if file.filename == '':
        return redirect(url_for('index', subfolder=subfolder))
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(application.config['UPLOAD_FOLDER'], subfolder, filename)
        file.save(save_path)
    return redirect(url_for('index', subfolder=subfolder))

@application.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(os.path.join(application.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        abort(404)

os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    application.run(debug=True)