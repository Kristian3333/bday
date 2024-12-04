from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-for-testing")

# In-memory cache for song status (moved from initiate_song.py)
SONG_CACHE = {}

# Generate lyrics route handler
@app.route("/api/generate-lyrics", methods=["POST"])
def generate_lyrics_route():
    try:
        data = request.json
        name = data.get('name', '').strip()
        hobbies = data.get('hobbies', '').strip()
        characteristics = data.get('characteristics', '').strip()

        if not all([name, hobbies, characteristics]):
            return jsonify({
                'error': 'Missing required fields'
            }), 400

        # OpenAI integration
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""Write a short, fun birthday song for {name}. 
        Include references to: {hobbies.split(',')[0]} and {characteristics.split(',')[0]}.
        Keep it to 2-3 short verses."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        lyrics = response.choices[0].message.content
        
        return jsonify({
            'lyrics': lyrics
        })

    except Exception as e:
        print(f"Error generating lyrics: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

# Initiate song route handler
@app.route("/api/initiate-song", methods=["POST"])
def initiate_song_route():
    try:
        data = request.json
        lyrics = data.get('lyrics')
        genre = data.get('genre', 'pop')
        tempo = data.get('tempo', 'medium')

        if not lyrics:
            return jsonify({'error': 'No lyrics provided'}), 400

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
        
        # Initialize tracking
        SONG_CACHE[tracking_id] = {
            'status': 'initiating',
            'created_at': datetime.now().isoformat(),
            'suno_id': None,
            'audio_url': None,
            'last_checked': datetime.now().isoformat()
        }

        response = requests.post(generate_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        generation_data = response.json()
        if isinstance(generation_data, list) and len(generation_data) > 0:
            suno_id = generation_data[0].get('id')
            if suno_id:
                SONG_CACHE[tracking_id]['suno_id'] = suno_id
                SONG_CACHE[tracking_id]['status'] = 'processing'
                return jsonify({
                    'tracking_id': tracking_id,
                    'status': 'processing'
                })

        return jsonify({
            'error': 'Failed to initiate song generation'
        }), 500

    except Exception as e:
        print(f"Error initiating song: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

# Check status route handler
@app.route("/api/check-status/<tracking_id>")
def check_status_route(tracking_id):
    try:
        if tracking_id not in SONG_CACHE:
            return jsonify({
                'status': 'failed',
                'message': 'Song not found'
            }), 404

        song_data = SONG_CACHE[tracking_id]
        
        if song_data['status'] == 'processing':
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
                            break
                    
                song_data['last_checked'] = datetime.now().isoformat()
                
            except Exception as e:
                print(f"Error checking Suno status: {str(e)}")

        return jsonify({
            'status': song_data['status'],
            'audio_url': song_data.get('audio_url'),
            'message': get_status_message(song_data['status'])
        })

    except Exception as e:
        print(f"Error in check_status: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

def get_status_message(status):
    messages = {
        'initiating': 'Initializing song generation...',
        'processing': 'Processing your song... This may take a minute...',
        'completed': 'Your song is ready!',
        'failed': 'Failed to generate song.'
    }
    return messages.get(status, 'Unknown status')

# Main routes
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/gallery")
def gallery():
    return render_template('gallery.html')

# Required for Vercel
app = app.wsgi_app