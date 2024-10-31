import os
from openai import OpenAI
import requests

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MUBERT_API_KEY = os.environ.get("MUBERT_API_KEY")
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

def generate_music(lyrics):
    try:
        # For now, return a placeholder URL since we don't have Mubert API
        return "https://example.com/placeholder-music.mp3"
        
        # Commenting out Mubert integration for now
        """
        headers = {
            "Authorization": f"Bearer {MUBERT_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "text": lyrics,
            "duration": 60,
            "style": "birthday_song"
        }
        response = requests.post(
            "https://api.mubert.com/v2/TTM",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()["data"]["url"]
        else:
            raise Exception("Music generation failed")
        """
    except Exception as e:
        print(f"Error generating music: {str(e)}")  # For debugging
        raise Exception(f"Failed to generate music. Please try again later.")
