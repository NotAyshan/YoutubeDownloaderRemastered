from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pathlib import Path
import os
import re
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DOWNLOAD_FOLDER = str(os.path.join(Path.home(), "Downloads/Youtube_download"))
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
#Evitar problemas con los nombres de videos para q windows reconozca el formato
def clean_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    errorType = 0
    if request.method == 'POST':
        link = request.form['video_url']
        download_type = request.form['download_type']
        try:\
            ##En teoria el usuario no va a poder ingresar otra cosa q no sea youtube
            validateVideoUrl = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            validVideoUrl = re.match(validateVideoUrl, link)
            if validVideoUrl:
                video = YouTube(link)
                if download_type == "mp3":
                    download = video.streams.filter(only_audio=True).first()
                elif download_type == "mp4":
                    download = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                else:
                    return redirect(url_for('index'))

                output_path = DOWNLOAD_FOLDER
                download.download(output_path)
                if download_type == "mp3":
                    download = video.streams.filter(only_audio=True).first()
                    download.download(output_path)
                    old_file_path = os.path.join(output_path, download.default_filename)
                    new_file_path = os.path.join(output_path, f"{clean_filename(video.title)}.mp3")
                    os.rename(old_file_path, new_file_path)
                    download_file = new_file_path
                else:
                    download_file = os.path.join(output_path, download.default_filename) 

                flash(f"Download completed: {download_file}", "success")
                return send_from_directory(output_path, os.path.basename(download_file), as_attachment=True)
            else:
                flash("Enter Valid YouTube Video URL!", "danger")
        except RegexMatchError:
            flash("No streams were found for the provided URL.", "danger")
        except Exception as e:
            flash(f"There was an error downloading the video: {str(e)}", "danger")

    return render_template('index.html')

@app.route('/about')
def about():
    return "Hello :) This is version 1.0 of the program Created by shad0wscr1pt3r."

if __name__ == '__main__':
    app.run(debug=True)
