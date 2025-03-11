from flask import Flask, request, jsonify, render_template, send_file
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


DOWNLOADS_FOLDER = "downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

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


@app.route("/download", methods=["GET"])
def download():
    id = request.args.get("id")
    filename = request.args.get("filename")

    print(id,filename)

    
    output_file = os.path.join(DOWNLOADS_FOLDER, filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_file,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',  # הוספת מטא-דאטה לקובץ ה-MP3
                'add_metadata': True,
                
                
            },
            {
                "key": "FFmpegThumbnailsConvertor",
                "format": "jpg",
                "when": "before_dl"
            }
        ],
        'writethumbnail': True,  # הורדת תמונת קאבר
        'embedthumbnail': True,   # הטמעת התמונה בקובץ
        'addmetadata': True,      # הוספת מטא-דאטה
        "ffmpeg-location": "./ffmpeg.exe",  # נתיב ל-FFmpeg
    }
    url = f"https://www.youtube.com/watch?v={id}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # הורד את הקובץ
    except:
        return jsonify("500")
        


    
    print(output_file)
    add_cover(output_file +".mp3", output_file+ ".jpg")
    os.remove(output_file+ ".jpg")
    
    if os.path.exists(output_file +".mp3"):
        return send_file(output_file +".mp3", as_attachment=True)
    else:
        return jsonify("500")
    
    # return jsonify({"message": "ההורדה הסתיימה בהצלחה!"})


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
