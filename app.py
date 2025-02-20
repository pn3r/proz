import os
import shutil
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()

# Get current time in Asia/Dhaka timezone
def get_current_time():
    tz = pytz.timezone('Asia/Dhaka')
    return datetime.now(tz).strftime("%d/%b/%Y %I:%M:%S %p")

# Function to log actions
def log_action(action, filename):
    log_entry = f"{get_current_time()} - {action}: {filename}\n"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

# Get free disk space in GB
def get_total_free_space():
    total, used, free = shutil.disk_usage(UPLOAD_FOLDER)
    return free / (1024 ** 3)

@app.route('/')
def index():
    # List uploaded files
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path) / 1024  # Size in KB
            files.append({'name': filename, 'size': round(size, 2)})

    # Read logs
    with open(LOG_FILE, "r") as log_file:
        logs = log_file.readlines()
    
    logs = [f"{idx + 1}. {line.strip()}" for idx, line in enumerate(logs)]
    total_free_space = get_total_free_space()

    return render_template('index.html', files=files, logs=logs, total_free_space=total_free_space)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    log_action("Uploaded", filename)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        log_action("Downloaded", filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        log_action("Deleted", filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
