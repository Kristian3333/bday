from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Song
from utils import generate_lyrics, generate_music

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_song():
    try:
        data = request.form
        name = data.get("name")
        hobbies = data.get("hobbies")
        characteristics = data.get("characteristics")
        genre = data.get("genre")
        tempo = data.get("tempo")
        pitch = data.get("pitch")
        complexity = data.get("complexity")

        # Generate lyrics using OpenAI
        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        # Generate music with selected genre and musical elements
        audio_url = generate_music(lyrics, genre, tempo=tempo, pitch=pitch, complexity=complexity)

        # Save to database
        song = Song(
            recipient_name=name,
            hobbies=hobbies,
            characteristics=characteristics,
            genre=genre,
            tempo=tempo,
            pitch=pitch,
            complexity=complexity,
            lyrics=lyrics,
            audio_url=audio_url
        )
        db.session.add(song)
        db.session.commit()

        return redirect(url_for('view_song', song_id=song.id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/song/<int:song_id>")
def view_song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template("song.html", song=song)
