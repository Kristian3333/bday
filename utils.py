import os
from openai import OpenAI
import requests

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_lyrics(name, hobbies, characteristics):
    try:
        prompt = f"""Write a birthday song lyrics for {name}. 
        Their hobbies are: {hobbies}
        Their characteristics are: {characteristics}
        Make it personal, fun and around 4 verses long."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better quality lyrics
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating lyrics: {str(e)}")  # For debugging
        raise Exception(f"Failed to generate lyrics. Please try again later.")

def generate_music(lyrics, genre, tempo="medium", pitch="medium", complexity="moderate"):
    try:
        # Format the prompt to include musical parameters
        prompt = f"""Create a {genre} style birthday song with the following characteristics:
        - Tempo: {tempo}
        - Pitch: {pitch}
        - Complexity: {complexity}
        
        Lyrics:
        {lyrics}
        
        Make it upbeat and celebratory, perfect for a birthday celebration."""

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        data = {
            "prompt": prompt,
            "make_instrumental": False,
            "model": "chirp-v3-5",
            "wait_audio": False
        }

        response = requests.post(
            "https://suno-api-livid-theta.vercel.app/api/generate",
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            if 'url' in result:
                return result['url']
            else:
                raise Exception("No audio URL in response")
        else:
            error_message = response.json().get('error', 'Unknown error occurred')
            raise Exception(f"API Error: {error_message}")

    except requests.RequestException as e:
        print(f"Network error: {str(e)}")  # For debugging
        raise Exception("Failed to connect to music generation service. Please try again later.")
    except Exception as e:
        print(f"Error generating music: {str(e)}")  # For debugging
        raise Exception("Failed to generate music. Please try again later.")
