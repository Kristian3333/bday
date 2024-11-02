from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from openai import OpenAI

# Update template directory configuration
app = Flask(__name__, 
           template_folder='../templates',  # Point to templates folder
           static_folder='../static')       # Point to static folder
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-for-testing")

# In-memory storage
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

@app.route("/")
def home():
    return """
    <h1>Birthday Song Generator</h1>
    <p>Welcome to the Birthday Song Generator!</p>
    <form action="/generate" method="POST">
        <div>
            <label>Name:</label>
            <input type="text" name="name" required>
        </div>
        <div>
            <label>Hobbies:</label>
            <input type="text" name="hobbies" required>
        </div>
        <div>
            <label>Characteristics:</label>
            <input type="text" name="characteristics" required>
        </div>
        <div>
            <label>Genre:</label>
            <select name="genre">
                <option value="pop">Pop</option>
                <option value="rock">Rock</option>
                <option value="jazz">Jazz</option>
            </select>
        </div>
        <div>
            <label>Tempo:</label>
            <select name="tempo">
                <option value="slow">Slow</option>
                <option value="medium">Medium</option>
                <option value="fast">Fast</option>
            </select>
        </div>
        <button type="submit">Generate Song</button>
    </form>
    """

@app.route("/gallery")
def gallery():
    songs_html = ""
    for song in example_songs:
        songs_html += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <h3>Song for {song['recipient_name']}</h3>
            <p>Genre: {song['genre']}</p>
            <p>Tempo: {song['tempo']}</p>
            <pre>{song['lyrics']}</pre>
        </div>
        """
    
    return f"""
    <h1>Song Gallery</h1>
    {songs_html}
    <p><a href="/">Create New Song</a></p>
    """

@app.route("/generate", methods=["POST"])
def generate_song():
    try:
        data = request.form
        name = data.get("name")
        hobbies = data.get("hobbies")
        characteristics = data.get("characteristics")
        genre = data.get("genre")
        tempo = data.get("tempo", "medium")
        pitch = data.get("pitch", "medium")
        complexity = data.get("complexity", "moderate")

        # Generate lyrics
        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        # Create song display
        return f"""
        <h1>Birthday Song for {name}</h1>
        <div style="margin: 20px 0;">
            <p><strong>Genre:</strong> {genre}</p>
            <p><strong>Tempo:</strong> {tempo}</p>
            <p><strong>Hobbies:</strong> {hobbies}</p>
            <p><strong>Characteristics:</strong> {characteristics}</p>
        </div>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 5px;">
            <h2>Lyrics:</h2>
            <pre>{lyrics}</pre>
        </div>
        <p><a href="/">Create Another Song</a></p>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

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

# Vercel handler
app = app.wsgi_app