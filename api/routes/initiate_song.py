from flask import request, jsonify
import requests
import uuid
from datetime import datetime

# In-memory cache for song status
SONG_CACHE = {}

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