import os, random, string
from zipfile import ZipFile 
from flask import Flask, request, send_file, Response
from youtube_dl import YoutubeDL
from flask_cors import CORS
from replit import db

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def home():
    response = Response(status = 200)
    return response

def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(length))

@app.route('/convert-mp3', methods = ['POST'])
def convert_mp3():
    link = request.get_json()['link']
    if not link.startswith('https://www.youtu') and not link.startswith('https://youtu') or 'channel' in link or 'user' in link:
        return {'message': 'error'}
    else:
        video_id = random_string(10)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{video_id}.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'}]
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                title = info_dict['title']
                db[f'{video_id}.mp3'] = title
            return {
                'message': 'success',
                'filename': f'{video_id}.mp3',
                'title': title,
            }
        except:
            return {'message': 'error'}

@app.route('/convert-mp4', methods = ['POST'])
def convert_mp4():
    link = request.get_json()['link']
    if not link.startswith('https://www.youtu') and not link.startswith('https://youtu') or 'channel' in link or 'user' in link:
        return {'message': 'error'}
    else:
        video_id = random_string(10)
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': f'{video_id}.mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'}]
        }
        try: 
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                title = info_dict['title']
                db[f'{video_id}.mp4'] = title
            return {
                'message': 'success',
                'filename': f'{video_id}.mp4',
                'title': title,
            }
        except:
            return {'message': 'error'}

@app.route('/convert-mp3-playlist', methods = ['POST'])
def convert_mp3_playlist():
    link = request.get_json()['link']
    if not link.startswith('https://www.youtu') and not link.startswith('https://youtu') or 'channel' in link or 'user' in link or 'list' not in link:
        return {'message': 'error'}
    else:
        try:
            video_urls = []
            with YoutubeDL() as ydl:
                result = ydl.extract_info(link, download=False)
                entries = result['entries']
                playlist_title = entries[0]['playlist']
                for i, item in enumerate(entries):
                    url = entries[i]['webpage_url']
                    video_urls.append(url)
            
            video_filenames = []
            for i in video_urls:
                video_id = random_string(10)
                ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{video_id}.mp3',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'}]
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(i, download=True)
                    title = info_dict['title']
                os.rename(f'{video_id}.mp3', f'{title}.mp3')
                video_filenames.append(f'{title}.mp3')

            zipfile_id = random_string(10)
            with ZipFile(f'{zipfile_id}.zip', 'w') as zip:
                for i in video_filenames:
                        zip.write(i)
                        os.remove(i)
                
            db[f'{zipfile_id}.zip'] = playlist_title

            return {
                    'message': 'success',
                    'filename': f'{zipfile_id}.zip',
                    'title': playlist_title,
            }
        except:
            return {'message': 'error'}
            
@app.route('/dl/<string:filename>')
def download(filename):
   title = db[filename]
   if filename.endswith('.mp3'):
        mimetype = 'audio/mpeg'
        ext = '.mp3'
   elif filename.endswith('.mp4'):
        mimetype = 'video/mp4'
        ext = '.mp4'
   elif filename.endswith('.zip'):
        mimetype = 'application/zip'
        ext = '.zip'
   result = send_file(filename, mimetype=mimetype, as_attachment=True, attachment_filename=f'{title}{ext}')
   os.remove(filename)
   del db[filename]
   return result

if __name__ == '__main__':
    app.run(host='0.0.0.0')