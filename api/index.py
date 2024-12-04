from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import requests
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# In-memory cache for songs
SONG_CACHE = {}

# HTML template (kept the same as before)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Birthday Song Generator</title>
    <style>
        body{font-family:Arial;margin:0;background:#f0f2f5;color:#333}
        .nav{padding:15px;background:white;border-bottom:1px solid #ddd}
        .nav a{color:#4CAF50;text-decoration:none;margin-right:20px}
        .container{max-width:800px;margin:20px auto;padding:0 20px}
        .card{background:white;padding:25px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px}
        .form-group{margin-bottom:20px}
        label{display:block;margin-bottom:8px;font-weight:bold}
        input,select{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;font-size:16px}
        button{background:#4CAF50;color:white;padding:12px 20px;border:none;border-radius:4px;cursor:pointer;width:100%;font-size:16px}
        button:hover{background:#45a049}
        .loading,.status-message{text-align:center;padding:20px;margin:20px 0;background:#e8f5e9;border-radius:4px;color:#4CAF50}
        .loading{display:none}
        .songs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;padding:20px 0}
        .song-card{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
        .lyrics{background:#f5f5f5;padding:15px;border-radius:4px;white-space:pre-wrap;margin:10px 0;font-family:monospace}
        @media (max-width:600px){.container{padding:0 15px}.card{padding:15px}.songs-grid{grid-template-columns:1fr}}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/">Home</a>
        <a href="/gallery">Gallery</a>
    </nav>
    <div class="container">
        {% if page == 'index' %}
            <div class="card">
                <h1>Birthday Song Generator</h1>
                <div class="form-group">
                    <label>Name:</label>
                    <input type="text" id="name" required>
                </div>
                <div class="form-group">
                    <label>Hobbies (comma-separated):</label>
                    <input type="text" id="hobbies" required>
                </div>
                <div class="form-group">
                    <label>Characteristics (comma-separated):</label>
                    <input type="text" id="characteristics" required>
                </div>
                <div class="form-group">
                    <label>Genre:</label>
                    <select id="genre">
                        <option value="pop">Pop</option>
                        <option value="rock">Rock</option>
                        <option value="jazz">Jazz</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Tempo:</label>
                    <select id="tempo">
                        <option value="slow">Slow</option>
                        <option value="medium">Medium</option>
                        <option value="fast">Fast</option>
                    </select>
                </div>
                <button id="generateButton">Generate Song</button>
                <div id="loading" class="loading">Generating your song... Please wait...</div>
            </div>
            <script>
                document.getElementById('generateButton').addEventListener('click', async () => {
                    const loading = document.getElementById('loading');
                    loading.style.display = 'block';
                    
                    try {
                        const lyricsResponse = await fetch('/api/generate-lyrics', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                name: document.getElementById('name').value,
                                hobbies: document.getElementById('hobbies').value,
                                characteristics: document.getElementById('characteristics').value
                            })
                        });
                        
                        const lyricsData = await lyricsResponse.json();
                        if (lyricsData.error) throw new Error(lyricsData.error);
                        
                        const songResponse = await fetch('/api/initiate-song', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                lyrics: lyricsData.lyrics,
                                genre: document.getElementById('genre').value,
                                tempo: document.getElementById('tempo').value
                            })
                        });
                        
                        const songData = await songResponse.json();
                        if (songData.error) throw new Error(songData.error);
                        
                        window.location.href = `/status?id=${songData.tracking_id}`;
                        
                    } catch (error) {
                        alert('Error: ' + error.message);
                        loading.style.display = 'none';
                    }
                });
            </script>
        {% elif page == 'status' %}
            <div class="card">
                <h1>Your Birthday Song</h1>
                <div id="status" class="status-message">Initializing song generation...</div>
                <div id="audioSection" style="display:none">
                    <h2>Your Song is Ready!</h2>
                    <audio id="audioPlayer" controls></audio>
                </div>
                <div id="lyricsSection">
                    <h2>Your Lyrics:</h2>
                    <div id="lyrics" class="lyrics"></div>
                </div>
                <div style="margin-top:20px">
                    <a href="/" style="text-decoration:none">
                        <button>Create Another Song</button>
                    </a>
                </div>
            </div>
            <script>
                const tracking_id = new URLSearchParams(window.location.search).get('id');
                const checkStatus = async () => {
                    try {
                        const response = await fetch(`/api/check-status/${tracking_id}`);
                        const data = await response.json();
                        
                        document.getElementById('status').textContent = data.message;
                        
                        if (data.status === 'completed' && data.audio_url) {
                            document.getElementById('audioPlayer').src = data.audio_url;
                            document.getElementById('audioSection').style.display = 'block';
                            return true;
                        }
                        return false;
                    } catch (error) {
                        console.error('Error:', error);
                        return false;
                    }
                };

                const pollStatus = async () => {
                    if (!await checkStatus()) {
                        setTimeout(pollStatus, 5000);
                    }
                };

                pollStatus();
            </script>
        {% else %}
            <div class="card">
                <h1>Song Gallery</h1>
                <div class="songs-grid">
                    <div class="song-card">
                        <h3>Song for John</h3>
                        <div class="song-details">
                            <strong>Genre:</strong> Rock<br>
                            <strong>Tempo:</strong> Medium
                        </div>
                        <div class="lyrics">
                            Happy birthday dear John,
                            The adventurer with a song in heart,
                            With your camera and guitar in hand,
                            Every day's a brand new start!
                        </div>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Routes
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, page='index')

@app.route("/status")
def status():
    return render_template_string(HTML_TEMPLATE, page='status')

@app.route("/gallery")
def gallery():
    return render_template_string(HTML_TEMPLATE, page='gallery')

@app.route("/api/generate-lyrics", methods=["POST"])
def generate_lyrics():
    try:
        data = request.json
        if not all(data.get(k, "").strip() for k in ["name", "hobbies", "characteristics"]):
            return jsonify({"error": "Missing required fields"}), 400

        client = OpenAI()  # Will automatically use OPENAI_API_KEY from environment

        prompt = f"""Write a short, fun birthday song for {data['name']}. 
        Include references to: {data['hobbies'].split(',')[0]} and {data['characteristics'].split(',')[0]}.
        Keep it to 2-3 short verses."""
        
        response = client.chat.completions.with_raw_response.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        completion = response.parse()
        return jsonify({"lyrics": completion.choices[0].message.content})
    except Exception as e:
        print(f"Error in generate_lyrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/initiate-song", methods=["POST"])
def initiate_song():
    try:
        data = request.json
        if not data.get("lyrics"):
            return jsonify({"error": "No lyrics provided"}), 400

        prompt = f"""Create a birthday song that resembles {data.get('genre', 'pop')} and has {data.get('tempo', 'medium')} tempo.
        Use these lyrics: {data['lyrics']}"""
        
        # Updated API configuration
        response = requests.post(
            "https://api.suno.ai/v1/generate",  # Updated endpoint
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('SUNO_API_KEY')}"  # Add API key if required
            },
            json={
                "prompt": prompt,
                "model": "bark-v2",  # Updated model name
                "make_instrumental": False,
                "duration": 30,  # Duration in seconds
                "sample_rate": 44100
            },
            timeout=15
        )
        
        print(f"Suno API Response Status: {response.status_code}")
        print(f"Suno API Response: {response.text}")
        
        if not response.ok:
            return jsonify({
                "error": f"Suno API error ({response.status_code}): {response.text}"
            }), response.status_code

        generation_data = response.json()
        tracking_id = str(uuid.uuid4())
        
        # Store the necessary information
        SONG_CACHE[tracking_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "task_id": generation_data.get("task_id", ""),
            "audio_url": None,
            "last_checked": datetime.now().isoformat()
        }
        
        return jsonify({
            "tracking_id": tracking_id,
            "status": "processing"
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/check-status/<tracking_id>")
def check_status(tracking_id):
    try:
        if tracking_id not in SONG_CACHE:
            return jsonify({"status": "failed", "message": "Song not found"}), 404

        song_data = SONG_CACHE[tracking_id]
        
        if song_data["status"] == "processing":
            try:
                response = requests.get(
                    f"https://api.suno.ai/v1/status/{song_data['task_id']}",
                    headers={
                        "Authorization": f"Bearer {os.getenv('SUNO_API_KEY')}"
                    },
                    timeout=10
                )
                
                if response.ok:
                    status_data = response.json()
                    if status_data.get("status") == "completed":
                        song_data["status"] = "completed"
                        song_data["audio_url"] = status_data.get("audio_url")
                    elif status_data.get("status") == "failed":
                        song_data["status"] = "failed"
                
            except Exception as e:
                print(f"Error checking status: {str(e)}")

        messages = {
            "initiating": "Initializing song generation...",
            "processing": "Processing your song... This may take a minute...",
            "completed": "Your song is ready!",
            "failed": "Failed to generate song."
        }
        
        return jsonify({
            "status": song_data["status"],
            "audio_url": song_data.get("audio_url"),
            "message": messages.get(song_data["status"], "Unknown status")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app.wsgi_app