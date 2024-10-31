import requests
import os

folder_path = r"C:\Users\krist\OneDrive\Desktop " 

url = "https://suno-api-livid-theta.vercel.app/api/generate"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
data = {
    "prompt": " ",
    "make_instrumental": False,
    "model": "chirp-v3-5|chirp-v3-0",
    "wait_audio": False
}

response = requests.post(url, headers=headers, json=data)

if response.ok:
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")

        
          