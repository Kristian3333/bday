from flask import jsonify
import requests
from datetime import datetime
from .initiate_song import SONG_CACHE

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