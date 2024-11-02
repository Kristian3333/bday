from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-for-testing")

# In-memory storage (note: this will reset on each serverless function call)
example_songs = [
    {
        "id": 1,
        "recipient_name": "John",
        "hobbies": "Playing guitar, hiking, photography",
        "characteristics": "Creative, adventurous, friendly",
        "genre": "rock",
        "tempo": "medium",
        "pitch": "medium",
        "complexity": "moderate",
        "lyrics": """Happy birthday dear John,
The adventurer with a song in heart,
With your camera and guitar in hand,
Every day's a brand new start!""",
        "audio_url": "https://example.com/rock-example.mp3",
        "is_example": True
    }
]

def generate_lyrics(name, hobbies, characteristics):
    try:
        if not os.environ.get("OPENAI_API_KEY"):
            raise Exception("No OpenAI API key")
            
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"""Write a birthday song lyrics for {name}. 
        Their hobbies are: {hobbies}
        Their characteristics are: {characteristics}
        Make it personal, fun and around 4 verses long."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback lyrics if OpenAI fails
        return f"""Happy Birthday dear {name},
On this special day of yours,
With your love for {hobbies.split(',')[0]},
And your {characteristics.split(',')[0]} ways!"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", songs=example_songs)

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

        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        new_song = {
            "id": len(example_songs) + 1,
            "recipient_name": name,
            "hobbies": hobbies,
            "characteristics": characteristics,
            "genre": genre,
            "tempo": tempo,
            "pitch": pitch,
            "complexity": complexity,
            "lyrics": lyrics,
            "audio_url": f"https://example.com/placeholder-{genre}-{tempo}.mp3",
            "is_example": False
        }
        
        # For demonstration, we'll show the generated song directly
        return render_template("song.html", song=new_song)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/song/<int:song_id>")
def view_song(song_id):
    song = next((song for song in example_songs if song["id"] == song_id), None)
    if song is None:
        return "Song not found", 404
    return render_template("song.html", song=song)

# This is the handler Vercel is looking for:
app = app.wsgi_app