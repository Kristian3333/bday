from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-for-testing")

# Import route handlers
from routes.generate_lyrics import generate_lyrics_route
from routes.initiate_song import initiate_song_route
from routes.check_status import check_status_route

# Register routes
app.route("/api/generate-lyrics", methods=["POST"])(generate_lyrics_route)
app.route("/api/initiate-song", methods=["POST"])(initiate_song_route)
app.route("/api/check-status/<tracking_id>")(check_status_route)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/gallery")
def gallery():
    return render_template('gallery.html')

# This line is required for Vercel
app = app.wsgi_app