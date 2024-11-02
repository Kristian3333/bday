from flask import Flask, request, jsonify
import os
from openai import OpenAI
import time
import requests
import json

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
            return generate_fallback_lyrics(name, hobbies, characteristics)
            
        openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            timeout=8
        )
        
        prompt = f"""Write a short, fun birthday song for {name}. 
        Include references to: {hobbies.split(',')[0]} and {characteristics.split(',')[0]}.
        Keep it to 2-3 short verses."""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        lyrics = response.choices[0].message.content
        if not lyrics:
            return generate_fallback_lyrics(name, hobbies, characteristics)
            
        return lyrics
    except Exception as e:
        print(f"OpenAI Error: {str(e)}")  # For debugging
        return generate_fallback_lyrics(name, hobbies, characteristics)

def generate_fallback_lyrics(name, hobbies, characteristics):
    try:
        # Safely get the first hobby and characteristic
        hobby = hobbies.split(',')[0].strip() if hobbies else "having fun"
        trait = characteristics.split(',')[0].strip() if characteristics else "wonderful"
        
        return f"""Happy Birthday dear {name}!
A special day for you to shine,
With your passion for {hobby},
And your {trait} spirit divine.

May your day be filled with joy,
And all your dreams come true,
Happy Birthday dear {name},
This song's especially for you!"""
    except Exception as e:
        # Ultimate fallback if everything fails
        return f"""Happy Birthday dear {name}!
On your special day,
May all your wishes come true,
In every possible way.

Happy Birthday to you,
May your dreams take flight,
Happy Birthday dear {name},
Make this day shine bright!"""

def generate_and_fetch_music(lyrics, genre, tempo):
    try:
        # First, generate the song
        generate_url = "https://suno-api-livid-theta.vercel.app/api/generate"
        prompt = f"""Create a birthday song that resembles {genre} and has {tempo} tempo.
        Use these lyrics:
        {lyrics}"""
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "make_instrumental": False,
            "model": "chirp-v3-5|chirp-v3-0",
            "wait_audio": False
        }
        
        response = requests.post(generate_url, headers=headers, json=data)
        
        if not response.ok:
            return None, "Failed to initiate song generation"
            
        # Get the song ID from the response
        generation_data = response.json()
        if not generation_data:
            return None, "No generation data received"
            
        song_id = generation_data.get('id')
        if not song_id:
            return None, "No song ID received"

        # Poll for the song status
        fetch_url = "https://suno-api-livid-theta.vercel.app/api/get"
        max_attempts = 12  # 60 seconds total (12 * 5 second intervals)
        attempts = 0
        
        while attempts < max_attempts:
            fetch_response = requests.get(fetch_url)
            if fetch_response.ok:
                songs = fetch_response.json()
                for song in songs:
                    if song.get('id') == song_id:
                        audio_url = song.get('audio_url')
                        if audio_url:
                            return song, None
            
            time.sleep(5)  # Wait 5 seconds before next attempt
            attempts += 1
        
        return None, "Timeout waiting for song generation"
            
    except Exception as e:
        return None, f"Error generating music: {str(e)}"

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Birthday Song Generator</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #45a049; }
            .nav { margin-bottom: 20px; }
            .loading { display: none; color: #666; margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 4px; text-align: center; }
            form.loading .loading { display: block; }
            form.loading button { display: none; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a> | 
            <a href="/gallery">Gallery</a>
        </div>
        <h1>Birthday Song Generator</h1>
        <form action="/generate" method="POST" onsubmit="return validateAndSubmit()">
            <div class="form-group">
                <label>Name:</label>
                <input type="text" name="name" required minlength="1">
            </div>
            <div class="form-group">
                <label>Hobbies (comma-separated):</label>
                <input type="text" name="hobbies" required minlength="1" placeholder="e.g., reading, swimming, painting">
            </div>
            <div class="form-group">
                <label>Characteristics (comma-separated):</label>
                <input type="text" name="characteristics" required minlength="1" placeholder="e.g., friendly, creative, energetic">
            </div>
            <div class="form-group">
                <label>Genre:</label>
                <select name="genre" required>
                    <option value="pop">Pop</option>
                    <option value="rock">Rock</option>
                    <option value="jazz">Jazz</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tempo:</label>
                <select name="tempo" required>
                    <option value="slow">Slow</option>
                    <option value="medium">Medium</option>
                    <option value="fast">Fast</option>
                </select>
            </div>
            <div class="loading">Generating your song... This will take about 30-60 seconds. Please wait...</div>
            <button type="submit">Generate Song</button>
        </form>

        <script>
        function validateAndSubmit() {
            const form = document.querySelector('form');
            const formData = new FormData(form);
            
            // Log form data
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }

            // Validate all required fields
            if (!formData.get('name') || !formData.get('hobbies') || !formData.get('characteristics')) {
                alert('Please fill out all required fields');
                return false;
            }

            // Show loading message
            document.querySelector('form').classList.add('loading');
            document.querySelector('.loading').innerHTML = 
                'Generating your song... This will take about 30-60 seconds. Please wait...';
            return true;
        }
        </script>
    </body>
    </html>
    """

@app.route("/gallery")
def gallery():
    songs_list = "".join([
        f"""
        <div style="border: 1px solid #ddd; margin: 10px; padding: 20px; border-radius: 4px;">
            <h3>Song for {song['recipient_name']}</h3>
            <p><strong>Genre:</strong> {song['genre']}</p>
            <p><strong>Tempo:</strong> {song['tempo']}</p>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px;">{song['lyrics']}</pre>
        </div>
        """
        for song in example_songs
    ])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Song Gallery</title>
        <style>
            body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            .nav {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a> | 
            <a href="/gallery">Gallery</a>
        </div>
        <h1>Song Gallery</h1>
        {songs_list}
    </body>
    </html>
    """

@app.route("/generate", methods=["POST"])
def generate_song():
    try:
        # Get form data and print for debugging
        data = request.form
        print("Received form data:", dict(data))  # Debug print
        
        name = data.get("name", "").strip()
        hobbies = data.get("hobbies", "").strip()
        characteristics = data.get("characteristics", "").strip()
        genre = data.get("genre", "pop").strip()
        tempo = data.get("tempo", "medium").strip()

        print(f"Processed data: name={name}, hobbies={hobbies}, characteristics={characteristics}, genre={genre}, tempo={tempo}")  # Debug print

        # Improved validation with better error message
        missing_fields = []
        if not name:
            missing_fields.append("Name")
        if not hobbies:
            missing_fields.append("Hobbies")
        if not characteristics:
            missing_fields.append("Characteristics")
            
        if missing_fields:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Missing Information</title>
                <style>
                    body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
                    .error {{ color: red; }}
                </style>
            </head>
            <body>
                <h1>Missing Information</h1>
                <p class="error">The following fields are required:</p>
                <ul>
                    {"".join(f"<li>{field}</li>" for field in missing_fields)}
                </ul>
                <p>Received data:</p>
                <ul>
                    <li>Name: {name}</li>
                    <li>Hobbies: {hobbies}</li>
                    <li>Characteristics: {characteristics}</li>
                    <li>Genre: {genre}</li>
                    <li>Tempo: {tempo}</li>
                </ul>
                <p><a href="/">← Back to Form</a></p>
            </body>
            </html>
            """, 400

        # Generate lyrics with error handling
        lyrics = generate_lyrics(name, hobbies, characteristics)
        if not lyrics:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error Generating Lyrics</h1>
                <p>Failed to generate lyrics. Please try again.</p>
                <p><a href="/">← Back to Form</a></p>
            </body>
            </html>
            """, 500
        
        # Generate and fetch music
        song_data, error = generate_and_fetch_music(lyrics, genre, tempo)
        
        if error:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error Generating Song</h1>
                <p>{error}</p>
                <p><a href="/">← Try Again</a></p>
            </body>
            </html>
            """, 500

        # Extract song details with default values
        audio_url = song_data.get('audio_url', '')
        generated_lyrics = song_data.get('lyric', lyrics)
        created_at = song_data.get('created_at', 'Unknown')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Birthday Song for {name}</title>
            <style>
                body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
                pre {{ background: #f5f5f5; padding: 20px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }}
                .nav {{ margin-bottom: 20px; }}
                .audio-player {{ width: 100%; margin: 20px 0; }}
                .audio-section {{ margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 4px; }}
                .song-info {{ margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="/">Home</a> | 
                <a href="/gallery">Gallery</a>
            </div>
            <h1>Birthday Song for {name}</h1>
            
            <div class="song-info">
                <p><strong>Genre:</strong> {genre}</p>
                <p><strong>Tempo:</strong> {tempo}</p>
                <p><strong>Created:</strong> {created_at}</p>
            </div>

            <div class="audio-section">
                <h2>Your Birthday Song:</h2>
                <audio controls class="audio-player">
                    <source src="{audio_url}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>

            <div>
                <h2>Generated Lyrics:</h2>
                <pre>{generated_lyrics}</pre>
            </div>

            <p><a href="/" style="text-decoration: none;">← Create Another Song</a></p>
            
            <script>
                // Auto-retry audio loading if it fails
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.querySelector('audio');
                    if (audio) {{
                        audio.onerror = function() {{
                            setTimeout(() => {{
                                audio.load();
                            }}, 2000);
                        }};
                    }}
                }});
            </script>
        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error</h1>
            <p>{str(e)}</p>
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """, 500

# This line is required for Vercel
app = app.wsgi_app