from flask import Flask, request
import os
from openai import OpenAI
import time

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
        # Set a timeout for the OpenAI API call
        start_time = time.time()
        timeout = 8  # 8 seconds timeout

        if not os.environ.get("OPENAI_API_KEY"):
            return generate_fallback_lyrics(name, hobbies, characteristics)
            
        openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            timeout=timeout
        )
        
        prompt = f"""Write a short, fun birthday song for {name}. 
        Include references to: {hobbies.split(',')[0]} and {characteristics.split(',')[0]}.
        Keep it to 2-3 short verses."""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 for faster response
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,  # Limiting response length
            temperature=0.7
        )
        
        # Check if we're approaching the timeout
        if time.time() - start_time > timeout:
            return generate_fallback_lyrics(name, hobbies, characteristics)
            
        return response.choices[0].message.content
    except Exception as e:
        return generate_fallback_lyrics(name, hobbies, characteristics)

def generate_fallback_lyrics(name, hobbies, characteristics):
    hobby = hobbies.split(',')[0].strip()
    trait = characteristics.split(',')[0].strip()
    
    return f"""Happy Birthday dear {name}!
A special day for you to shine,
With your passion for {hobby},
And your {trait} spirit divine.

May your day be filled with joy,
And all your dreams come true,
Happy Birthday dear {name},
This song's especially for you!"""

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
            .loading { display: none; }
            form.loading .loading { display: block; }
            form.loading button { display: none; }
        </style>
        <script>
            function showLoading() {
                document.querySelector('form').classList.add('loading');
                return true;
            }
        </script>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a> | 
            <a href="/gallery">Gallery</a>
        </div>
        <h1>Birthday Song Generator</h1>
        <form action="/generate" method="POST" onsubmit="return showLoading()">
            <div class="form-group">
                <label>Name:</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Hobbies (comma-separated):</label>
                <input type="text" name="hobbies" required placeholder="e.g., reading, swimming, painting">
            </div>
            <div class="form-group">
                <label>Characteristics (comma-separated):</label>
                <input type="text" name="characteristics" required placeholder="e.g., friendly, creative, energetic">
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
            <div class="loading">Generating your song... Please wait...</div>
            <button type="submit">Generate Song</button>
        </form>
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
        data = request.form
        name = data.get("name")
        hobbies = data.get("hobbies")
        characteristics = data.get("characteristics")
        genre = data.get("genre")
        tempo = data.get("tempo", "medium")

        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Birthday Song for {name}</title>
            <style>
                body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
                pre {{ background: #f5f5f5; padding: 20px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }}
                .nav {{ margin-bottom: 20px; }}
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