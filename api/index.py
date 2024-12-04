from flask import Flask, request, jsonify
import os
from openai import OpenAI
import time
import requests
import json
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-for-testing")

# In-memory song cache
SONG_CACHE = {}

def generate_lyrics(name, hobbies, characteristics):
    """Generate lyrics using a template"""
    try:
        hobby = hobbies.split(',')[0].strip().lower() if hobbies else "having fun"
        trait = characteristics.split(',')[0].strip().lower() if characteristics else "wonderful"
        
        return f"""Happy Birthday dear {name}!
A special day for you to shine,
With your passion for {hobby},
And your {trait} spirit divine.

May your day be filled with joy,
And all your dreams come true,
Happy Birthday dear {name},
This song's especially for you!"""
    except Exception as e:
        print(f"Error in lyrics generation: {str(e)}")
        return f"""Happy Birthday dear {name}!
On your special day,
May all your wishes come true,
In every possible way."""

def initiate_song_generation(lyrics, genre, tempo):
    """Initiate song generation and return a tracking ID"""
    tracking_id = None
    try:
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
        
        tracking_id = str(uuid.uuid4())
        
        # Store initial data in cache
        SONG_CACHE[tracking_id] = {
            'status': 'initiating',
            'lyrics': lyrics,
            'genre': genre,
            'tempo': tempo,
            'created_at': time.time(),
            'suno_id': None,
            'audio_url': None,
            'last_checked': time.time()
        }
        
        response = requests.post(generate_url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            generation_data = response.json()
            if isinstance(generation_data, list) and len(generation_data) > 0:
                suno_id = generation_data[0].get('id')
                if suno_id:
                    SONG_CACHE[tracking_id]['suno_id'] = suno_id
                    SONG_CACHE[tracking_id]['status'] = 'processing'
                    return tracking_id
                    
        # If we get here, something went wrong
        if tracking_id:
            SONG_CACHE[tracking_id]['status'] = 'failed'
        return tracking_id
        
    except Exception as e:
        print(f"Error initiating song generation: {str(e)}")
        if tracking_id:
            SONG_CACHE[tracking_id]['status'] = 'failed'
        return tracking_id

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Birthday Song Generator</title>
        <style>
            body { 
                font-family: Arial; 
                max-width: 800px; 
                margin: 20px auto; 
                padding: 0 20px; 
                background-color: #f0f2f5;
            }
            .form-group { 
                margin-bottom: 15px; 
            }
            label { 
                display: block; 
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select { 
                width: 100%; 
                padding: 8px; 
                margin-bottom: 10px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                font-size: 16px;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #4CAF50;
                box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
            }
            button { 
                background-color: #4CAF50; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover { 
                background-color: #45a049; 
            }
            .nav { 
                margin-bottom: 20px;
                padding: 10px 0;
                border-bottom: 1px solid #ddd;
            }
            .nav a {
                color: #4CAF50;
                text-decoration: none;
                margin-right: 20px;
            }
            .nav a:hover {
                color: #45a049;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .loading { 
                display: none; 
                text-align: center;
                padding: 20px;
                margin: 20px 0;
                background: #e8f5e9;
                border-radius: 4px;
                color: #2e7d32;
            }
            form.loading .loading { 
                display: block; 
            }
            form.loading button { 
                display: none; 
            }
            .error {
                color: red;
                margin-top: 5px;
                font-size: 14px;
                display: none;
            }
            input:invalid + .error {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/gallery">Gallery</a>
        </div>
        
        <div class="card">
            <h1 style="text-align: center; color: #333;">Birthday Song Generator</h1>
            
            <form method="POST" action="/generate">
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input 
                        type="text" 
                        id="name" 
                        name="name" 
                        required 
                        placeholder="Enter the birthday person's name"
                    >
                    <div class="error">Please enter a name</div>
                </div>

                <div class="form-group">
                    <label for="hobbies">Hobbies (comma-separated):</label>
                    <input 
                        type="text" 
                        id="hobbies" 
                        name="hobbies" 
                        required 
                        placeholder="e.g., reading, swimming, painting"
                    >
                    <div class="error">Please enter at least one hobby</div>
                </div>

                <div class="form-group">
                    <label for="characteristics">Characteristics (comma-separated):</label>
                    <input 
                        type="text" 
                        id="characteristics" 
                        name="characteristics" 
                        required 
                        placeholder="e.g., friendly, creative, energetic"
                    >
                    <div class="error">Please enter at least one characteristic</div>
                </div>

                <div class="form-group">
                    <label for="genre">Genre:</label>
                    <select id="genre" name="genre" required>
                        <option value="pop">Pop</option>
                        <option value="rock">Rock</option>
                        <option value="jazz">Jazz</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="tempo">Tempo:</label>
                    <select id="tempo" name="tempo" required>
                        <option value="slow">Slow</option>
                        <option value="medium">Medium</option>
                        <option value="fast">Fast</option>
                    </select>
                </div>

                <div class="loading">
                    Generating your song... This will take about 30-60 seconds. Please wait...
                </div>

                <button type="submit">Generate Song</button>
            </form>
        </div>

        <script>
            document.querySelector('form').addEventListener('submit', function(e) {
                const form = this;
                const name = form.querySelector('#name').value.trim();
                const hobbies = form.querySelector('#hobbies').value.trim();
                const characteristics = form.querySelector('#characteristics').value.trim();
                
                if (!name || !hobbies || !characteristics) {
                    e.preventDefault();
                    alert('Please fill out all required fields');
                    return false;
                }
                
                form.classList.add('loading');
                return true;
            });

            // Modified input handling to allow spaces while preventing multiple consecutive spaces
            document.querySelectorAll('input[type="text"]').forEach(input => {
                input.addEventListener('input', function() {
                    // Replace multiple consecutive spaces with a single space
                    this.value = this.value.replace(/\s+/g, ' ');
                });

                // Clean up on blur (when input loses focus)
                input.addEventListener('blur', function() {
                    this.value = this.value.trim();
                });
            });
        </script>
    </body>
    </html>
    """

@app.route("/gallery")
def gallery():
    example_songs = [
        {
            "id": 1,
            "recipient_name": "John",
            "genre": "rock",
            "tempo": "medium",
            "lyrics": """Happy birthday dear John,
The adventurer with a song in heart,
With your camera and guitar in hand,
Every day's a brand new start!"""
        }
    ]
    
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
        name = str(request.form.get('name', '')).strip()
        hobbies = str(request.form.get('hobbies', '')).strip()
        characteristics = str(request.form.get('characteristics', '')).strip()
        genre = str(request.form.get('genre', 'pop')).strip()
        tempo = str(request.form.get('tempo', 'medium')).strip()

        print(f"Processing request for {name} with genre {genre} and tempo {tempo}")

        # Generate lyrics
        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        # Initiate song generation
        tracking_id = initiate_song_generation(lyrics, genre, tempo)
        
        # Return the waiting page with tracking ID
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Generating Your Song</title>
            <style>
                body {{ 
                    font-family: Arial; 
                    max-width: 800px; 
                    margin: 20px auto; 
                    padding: 20px;
                    background-color: #f0f2f5;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .status {{
                    text-align: center;
                    padding: 20px;
                    margin: 20px 0;
                    background: #e8f5e9;
                    border-radius: 4px;
                }}
                .lyrics {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    white-space: pre-wrap;
                }}
                .nav {{
                    margin-bottom: 20px;
                }}
                .nav a {{
                    color: #4CAF50;
                    text-decoration: none;
                    margin-right: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="nav">
                    <a href="/">← Back to Home</a>
                </div>
                
                <h1>Generating Your Birthday Song</h1>
                
                <div id="status" class="status">
                    Initializing song generation...
                </div>
                
                <div id="audioSection" style="display: none;">
                    <h2>Your Song</h2>
                    <audio controls style="width: 100%">
                        <source id="audioSource" src="" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                
                <div>
                    <h2>Your Lyrics:</h2>
                    <div class="lyrics">{lyrics}</div>
                </div>
                
                <script>
                    const trackingId = '{tracking_id}';
                    let attempts = 0;
                    const maxAttempts = 40;
                    
                    function checkStatus() {{
                        if (attempts >= maxAttempts) {{
                            document.getElementById('status').innerHTML = 
                                'Song generation is taking longer than expected. Please <a href="/">try again</a>.';
                            return;
                        }}
                        
                        fetch(`/check_status/${{trackingId}}`)
                            .then(response => response.json())
                            .then(data => {{
                                document.getElementById('status').textContent = data.message;
                                
                                if (data.status === 'completed' && data.audio_url) {{
                                    document.getElementById('status').style.display = 'none';
                                    document.getElementById('audioSection').style.display = 'block';
                                    document.getElementById('audioSource').src = data.audio_url;
                                    document.querySelector('audio').load();
                                }} else if (data.status === 'failed') {{
                                    document.getElementById('status').innerHTML = 
                                        'Failed to generate song. Please <a href="/">try again</a>.';
                                }} else {{
                                    attempts++;
                                    setTimeout(checkStatus, 5000);
                                }}
                            }})
                            .catch(error => {{
                                console.error('Error:', error);
                                attempts++;
                                setTimeout(checkStatus, 5000);
                            }});
                    }}
                    
                    checkStatus();
                </script>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        print(f"Error in generate_song: {str(e)}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 20px; }}
                .error {{ color: red; padding: 20px; background: #fff3f3; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>Error</h1>
            <div class="error">
                <p>Failed to process your request. Please try again.</p>
                <p>Error details: {str(e)}</p>
            </div>
            <p><a href="/">← Try Again</a></p>
        </body>
        </html>
        """

@app.route("/check_status/<tracking_id>")
def check_status(tracking_id):
    """Check the status of song generation"""
    try:
        if tracking_id not in SONG_CACHE:
            return jsonify({
                'status': 'failed',
                'message': 'Song not found. Please try again.'
            })

        song_data = SONG_CACHE[tracking_id]
        current_time = time.time()
        
        # Only check Suno API every 5 seconds
        if song_data['status'] == 'processing' and current_time - song_data['last_checked'] >= 5:
            try:
                fetch_url = "https://suno-api-livid-theta.vercel.app/api/get"
                response = requests.get(fetch_url, timeout=10)
                
                if response.ok:
                    songs = response.json()
                    for song in songs:
                        if song.get('id') == song_data['suno_id']:
                            status = song.get('status', 'unknown')
                            if status == 'completed' and song.get('audio_url'):
                                song_data['status'] = 'completed'
                                song_data['audio_url'] = song.get('audio_url')
                            elif status == 'failed':
                                song_data['status'] = 'failed'
                            break  # Exit loop once we find our song
                            
            except Exception as e:
                print(f"Error checking Suno status: {str(e)}")
            
            song_data['last_checked'] = current_time

        status_messages = {
            'initiating': 'Initializing song generation...',
            'processing': 'Processing your song... This may take a minute...',
            'completed': 'Your song is ready!',
            'failed': 'Failed to generate song.'
        }

        return jsonify({
            'status': song_data['status'],
            'message': status_messages.get(song_data['status'], 'Processing...'),
            'audio_url': song_data.get('audio_url')
        })

    except Exception as e:
        print(f"Error in check_status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error checking status'
        })

# This line is required for Vercel
app = app.wsgi_app