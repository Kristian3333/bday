from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Song
from utils import generate_lyrics, generate_music

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    # Get all example songs from the database
    songs = Song.query.filter_by(is_example=True).all()
    return render_template("gallery.html", songs=songs)

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

def create_example_songs():
    example_songs = [
        {
            "recipient_name": "John",
            "hobbies": "Playing guitar, hiking, photography",
            "characteristics": "Creative, adventurous, friendly",
            "genre": "rock",
            "tempo": "medium",
            "pitch": "medium",
            "complexity": "moderate",
            "lyrics": """Happy birthday dear John,
The adventurer with a song in his heart,
With your camera and guitar in hand,
Every day's a brand new start!

Climbing mountains, chasing dreams,
Your spirit wild and free,
Through your lens the world gleams,
What a joy it is to be!""",
            "audio_url": "https://example.com/rock-example.mp3"
        },
        {
            "recipient_name": "Sarah",
            "hobbies": "Dancing, painting, gardening",
            "characteristics": "Artistic, graceful, nurturing",
            "genre": "pop",
            "tempo": "fast",
            "pitch": "high",
            "complexity": "complex",
            "lyrics": """It's your special day, dear Sarah divine,
Your garden of colors making life so fine,
Dancing through life with grace and flair,
Spreading joy beyond compare!

With every brushstroke, you paint your way,
Making the world brighter day by day,
Your gentle soul helps flowers grow,
Happy birthday to you, you're quite a show!""",
            "audio_url": "https://example.com/pop-example.mp3"
        },
        {
            "recipient_name": "Mike",
            "hobbies": "Basketball, cooking, reading",
            "characteristics": "Athletic, creative, intellectual",
            "genre": "hiphop",
            "tempo": "fast",
            "pitch": "low",
            "complexity": "complex",
            "lyrics": """Yo Mike, it's your birthday, time to celebrate,
On the court you're showing skills that are first-rate,
In the kitchen cooking up a storm,
While reading tales that break the norm!

Books and balls, that's how you roll,
Creative mind and athletic soul,
Happy birthday to the MVP,
The coolest chef that we ever see!""",
            "audio_url": "https://example.com/hiphop-example.mp3"
        }
    ]

    for song_data in example_songs:
        song = Song(
            recipient_name=song_data["recipient_name"],
            hobbies=song_data["hobbies"],
            characteristics=song_data["characteristics"],
            genre=song_data["genre"],
            tempo=song_data["tempo"],
            pitch=song_data["pitch"],
            complexity=song_data["complexity"],
            lyrics=song_data["lyrics"],
            audio_url=song_data["audio_url"],
            is_example=True
        )
        db.session.add(song)
    
    db.session.commit()
