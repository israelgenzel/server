import time
from flask import Flask, after_this_request, request, jsonify, render_template, send_file
from flask_cors import CORS
import requests
from ytmusicapi import YTMusic
import yt_dlp
import os
from embed_thumb import add_cover

# הגדרה ראשונית
app = Flask(__name__)
CORS(app)  # מאפשר גישה מכל דומיין

yt = YTMusic()


DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")  # דף הבית עם תיבת החיפוש

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "חובה להזין מילת חיפוש"}), 400

    artists =  yt.search(query=query,limit=6,filter="artists")
    artists_list=[]
    for artist in artists:
        artists_list.append({
            "id": artist["browseId"],
            "name":artist["artist"],
            "resultType": artist["resultType"],
            "thumbnails": "./src/assets/default-image.jpg",
           


        })
    
    return jsonify(artists_list)

@app.route('/download', methods=['GET'])
def download_video():
    print("download_video")
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "Missing video URL"}), 400
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'writethumbnail': False,  # הורדת תמונת קאבר
            'embedthumbnail': False,   # הטמעת התמונה בקובץ
        }
      

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # מציאת הקובץ שהורד
        downloaded_files = os.listdir(DOWNLOAD_FOLDER)
        print(downloaded_files)
        if not downloaded_files:
            return jsonify({"error": "Download failed"}), 500

        print(f"✅ הורדה הושלמה: {downloaded_files[0]}")
        filename = os.path.join(DOWNLOAD_FOLDER, downloaded_files[0])

        # מחיקת הקובץ אחרי שליחה
        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(filename):
                    time.sleep(1)  # חכה שנייה לוודא שהשליחה הסתיימה
                    os.remove(filename)
                    print(f"🗑️ קובץ נמחק: {filename}")
            except Exception as e:
                print(f"⚠️ שגיאה במחיקה: {e}")
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_info", methods=["GET"])
def get_info():
    # קבלת URL מהמשתמש 
    id = request.args.get("id")
    resultType = request.args.get("resultType").lower()
    print(resultType)
    match resultType:
        case "artist":
            artist_info = yt.get_artist(id)
            albums_list =[]
            albums = yt.get_artist_albums(artist_info["albums"]["browseId"],artist_info["albums"]["params"])
            for album in albums:
                albums_list.append({
                    "id": album["browseId"],
                    "name":album["title"],
                    "resultType": album["type"],
                    "thumbnails": album["thumbnails"][0]["url"] or  "./src/assets/default-image.jpg",
                })
            return jsonify(albums_list)
        case "album":
            print("1")
            album_info = yt.get_album(id)
            # print(album_info)
            tracks_list =[]
            tracks = album_info["tracks"]
            for track in tracks:
                thumbnails = "./src/assets/default-image.jpg"
                if(track.get("thumbnails")):
                    thumbnails = track["thumbnails"][0]["url"]
                tracks_list.append({
                    "id": track["videoId"],
                    "name":track["title"],
                    "resultType": "track",
                    "thumbnails": thumbnails
                })
            return jsonify(tracks_list)
    return
            

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
