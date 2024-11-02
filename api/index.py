from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
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
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Birthday Song Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input, select {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            .nav {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a> | 
            <a href="/gallery">Gallery</a>
        </div>
        <h1>Birthday Song Generator</h1>
        <form action="/generate" method="POST">
            <div class="form-group">
                <label>Name:</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Hobbies:</label>
                <input type="text" name="hobbies" required>
            </div>
            <div class="form-group">
                <label>Characteristics:</label>
                <input type="text" name="characteristics" required>
            </div>
            <div class="form-group">
                <label>Genre:</label>
                <select name="genre">
                    <option value="pop">Pop</option>
                    <option value="rock">Rock</option>
                    <option value="jazz">Jazz</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tempo:</label>
                <select name="tempo">
                    <option value="slow">Slow</option>
                    <option value="medium">Medium</option>
                    <option value="fast">Fast</option>
                </select>
            </div>
            <button type="submit">Generate Song</button>
        </form>
    </body>
    </html>
    """
    return html_content

@app.route("/gallery")
def gallery():
    songs_html = ""
    for song in example_songs:
        songs_html += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 20px; border-radius: 4px;">
            <h3>Song for {song['recipient_name']}</h3>
            <p><strong>Genre:</strong> {song['genre']}</p>
            <p><strong>Tempo:</strong> {song['tempo']}</p>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px;">{song['lyrics']}</pre>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Song Gallery</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .nav {{
                margin-bottom: 20px;
            }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a> | 
            <a href="/gallery">Gallery</a>
        </div>
        <h1>Song Gallery</h1>
        {songs_html}
    </body>
    </html>
    """
    return html_content

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

        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Birthday Song for {name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .nav {{
                    margin-bottom: 20px;
                }}
                pre {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 4px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="/">Home</a> | 
                <a href="/gallery">Gallery</a>
            </div>
            <h1>Birthday Song for {name}</h1>
            <div style="margin: 20px 0;">
                <p><strong>Genre:</strong> {genre}</p>
                <p><strong>Tempo:</strong> {tempo}</p>
                <p><strong>Hobbies:</strong> {hobbies}</p>
                <p><strong>Characteristics:</strong> {characteristics}</p>
            </div>
            <div>
                <h2>Lyrics:</h2>
                <pre>{lyrics}</pre>
            </div>
            <p><a href="/" style="text-decoration: none;">← Create Another Song</a></p>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        return f"Error: {str(e)}", 500

# Vercel handler
app = app.wsgi_app