from flask import request, jsonify
from openai import OpenAI
import os

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