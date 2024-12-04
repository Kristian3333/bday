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
        return f"""Happy Birthday dear {name}!
On your special day,
May all your wishes come true,
In every possible way."""

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
        
        # Generate the song
        print("Initiating song generation...")
        response = requests.post(generate_url, headers=headers, json=data)
        
        if not response.ok:
            return None, "Failed to initiate song generation"
            
        # Get the song ID from the response
        generation_data = response.json()
        print("Generation response:", generation_data)
        
        if isinstance(generation_data, list) and len(generation_data) > 0:
            song_id = generation_data[0].get('id')
            initial_song = generation_data[0]  # Store the initial song data
        else:
            return None, "No valid song ID received"

        if not song_id:
            return None, "No song ID received"

        print(f"Generated song ID: {song_id}")

        # Poll for the song status
        fetch_url = "https://suno-api-livid-theta.vercel.app/api/get"
        max_attempts = 40  # 200 seconds total (40 * 5 second intervals)
        attempts = 0
        
        valid_statuses = {
            'submitted': 'Song has been submitted for processing...',
            'queued': 'Song is in the queue...',
            'processing': 'Processing your song...',
            'streaming': 'Almost there, finalizing your song...',
            'completed': 'Song is ready!',
        }
        
        while attempts < max_attempts:
            fetch_response = requests.get(fetch_url)
            print(f"Fetch attempt {attempts + 1}, status: {fetch_response.status_code}")
            
            if fetch_response.ok:
                songs = fetch_response.json()
                if not isinstance(songs, list):
                    print(f"Unexpected response format: {songs}")
                    continue
                    
                for song in songs:
                    if song.get('id') == song_id:
                        status = song.get('status', 'unknown')
                        print(f"Found song. Status: {status}")
                        
                        # If we have a completed song with audio_url, return it
                        if status == 'completed' and song.get('audio_url'):
                            print(f"Song completed successfully: {song.get('audio_url')}")
                            return song, None
                            
                        # If the song has failed, return error
                        if status == 'failed':
                            print("Song generation failed")
                            return None, "Song generation failed. Please try again."
                            
                        # For other statuses, print progress and continue waiting
                        if status in valid_statuses:
                            print(valid_statuses[status])
                        else:
                            print(f"Current status: {status}")
            
            time.sleep(5)
            attempts += 1
            print(f"Waiting... Attempt {attempts} of {max_attempts}")
            
            # Every 5 attempts (25 seconds), print a progress message
            if attempts % 5 == 0:
                print(f"Still working... ({attempts * 5} seconds elapsed)")
        
        # If we get here, we've timed out. Return the last status we had
        return None, "Song generation is taking longer than expected. Please try again."
            
    except Exception as e:
        print(f"Exception in generate_and_fetch_music: {str(e)}")
        return None, f"Error generating music: {str(e)}"
    
@app.route("/check_status/<song_id>")
def check_status(song_id):
    try:
        fetch_url = "https://suno-api-livid-theta.vercel.app/api/get"
        response = requests.get(fetch_url)
        
        if response.ok:
            songs = response.json()
            for song in songs:
                if song.get('id') == song_id:
                    return jsonify({
                        'status': song.get('status', 'unknown'),
                        'audio_url': song.get('audio_url', '')
                    })
                    
        return jsonify({'status': 'not_found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
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
        # Get the raw form data and print it
        form_data = request.form
        print("Form data received:", dict(request.form))

        # Get form data with explicit type conversion and debugging
        name = str(request.form.get('name', ''))
        hobbies = str(request.form.get('hobbies', ''))
        characteristics = str(request.form.get('characteristics', ''))
        genre = str(request.form.get('genre', 'pop'))
        tempo = str(request.form.get('tempo', 'medium'))

        print(f"""
        Debug received values:
        name: '{name}'
        hobbies: '{hobbies}'
        characteristics: '{characteristics}'
        genre: '{genre}'
        tempo: '{tempo}'
        """)

        # Check for empty values after stripping whitespace
        name = name.strip()
        hobbies = hobbies.strip()
        characteristics = characteristics.strip()
        
        print(f"After stripping - name: '{name}', hobbies: '{hobbies}', characteristics: '{characteristics}'")

        # Validate all required fields
        if not name or not hobbies or not characteristics:
            error_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Form Data Error</title>
                <style>
                    body {{ font-family: Arial; max-width: 800px; margin: 20px auto; padding: 20px; }}
                    .error {{ color: red; }}
                    .debug {{ background: #f5f5f5; padding: 15px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <h1>Form Data Error</h1>
                <div class="error">
                    <p>The following fields are missing or empty:</p>
                    <ul>
                        {f"<li>Name</li>" if not name else ""}
                        {f"<li>Hobbies</li>" if not hobbies else ""}
                        {f"<li>Characteristics</li>" if not characteristics else ""}
                    </ul>
                </div>
                
                <div class="debug">
                    <h3>Debug Information:</h3>
                    <p>Raw form data: {dict(request.form)}</p>
                    <p>Processed values:</p>
                    <ul>
                        <li>Name: '{name}'</li>
                        <li>Hobbies: '{hobbies}'</li>
                        <li>Characteristics: '{characteristics}'</li>
                        <li>Genre: '{genre}'</li>
                        <li>Tempo: '{tempo}'</li>
                    </ul>
                    <p>Request Method: {request.method}</p>
                    <p>Content Type: {request.content_type}</p>
                </div>
                
                <p><a href="/">← Back to Form</a></p>
            </body>
            </html>
            """
            return error_message, 400

        # If we get here, all required fields are present
        print("All required fields present, generating lyrics...")

        # Generate lyrics
        lyrics = generate_lyrics(name, hobbies, characteristics)
        if not lyrics:
            raise Exception("Failed to generate lyrics")

        print("Lyrics generated, generating music...")

        # Generate and fetch music
        song_data, error = generate_and_fetch_music(lyrics, genre, tempo)
        
        if error:
            raise Exception(f"Music generation error: {error}")

        print("Music generated successfully")

        # Extract song details
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
                .status {{ padding: 10px; margin: 10px 0; text-align: center; }}
                .loading {{ display: block; text-align: center; padding: 20px; }}
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

            <div id="status" class="status">
                Generating your song... This may take a minute...
            </div>

            <div class="audio-section" id="audioSection" style="display: none;">
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
                const songId = '{song_id}';
                const statusElement = document.getElementById('status');
                const audioSection = document.getElementById('audioSection');
                
                function checkStatus() {{
                    fetch(`/check_status/${{songId}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'completed' && data.audio_url) {{
                                statusElement.style.display = 'none';
                                audioSection.style.display = 'block';
                                document.querySelector('audio').src = data.audio_url;
                            }} else if (data.status === 'failed') {{
                                statusElement.textContent = 'Song generation failed. Please try again.';
                            }} else {{
                                statusElement.textContent = `Status: ${{data.status}}...`;
                                setTimeout(checkStatus, 5000);
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            statusElement.textContent = 'Error checking status. Please refresh the page.';
                        }});
                }}

                checkStatus();
            </script>
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
                .error {{ color: red; padding: 10px; background: #fff3f3; border-radius: 4px; margin: 10px 0; }}
                .debug {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 4px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <h1>Processing Error</h1>
            <div class="error">
                <strong>Error Details:</strong>
                <pre>{str(e)}</pre>
            </div>
            
            <div class="debug">
                <h3>Debug Information:</h3>
                <p><strong>Form Data:</strong></p>
                <pre>{json.dumps(dict(request.form), indent=2)}</pre>
                <p><strong>Request Method:</strong> {request.method}</p>
                <p><strong>Content Type:</strong> {request.content_type}</p>
            </div>
            
            <p><a href="/" style="text-decoration: none; color: #4CAF50;">← Try Again</a></p>
        </body>
        </html>
        """, 500

# This line is required for Vercel
app = app.wsgi_app