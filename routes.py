from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Song
from utils import generate_lyrics, generate_music

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_song():
    try:
        data = request.form
        name = data.get("name")
        hobbies = data.get("hobbies")
        characteristics = data.get("characteristics")
        genre = data.get("genre")

        # Generate lyrics using OpenAI
        lyrics = generate_lyrics(name, hobbies, characteristics)
        
        # Generate music with selected genre
        audio_url = generate_music(lyrics, genre)

        # Save to database
        song = Song(
            recipient_name=name,
            hobbies=hobbies,
            characteristics=characteristics,
            genre=genre,
            lyrics=lyrics,
            audio_url=audio_url
        )
        db.session.add(song)
        db.session.commit()

        return redirect(url_for('view_song', song_id=song.id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/song/<int:song_id>")
def view_song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template("song.html", song=song)

# Payment-related routes commented out
"""
@app.route("/create-payment-intent/<int:song_id>")
def create_payment_intent(song_id):
    try:
        song = Song.query.get_or_404(song_id)
        
        if song.payment_status != 'pending':
            return jsonify({"error": "Song already purchased"}), 400

        intent = stripe.PaymentIntent.create(
            amount=499,  # Amount in cents
            currency='usd',
            metadata={'song_id': song_id}
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payment-success")
def payment_success():
    payment_intent_id = request.args.get('payment_intent')
    if payment_intent_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            song_id = payment_intent.metadata.get('song_id')
            
            if song_id:
                song = Song.query.get(song_id)
                if song:
                    song.payment_status = 'completed'
                    song.stripe_payment_id = payment_intent_id
                    db.session.commit()
                    return render_template("payment_success.html", song=song)
        except Exception as e:
            print(f"Error processing payment success: {str(e)}")
    
    return redirect(url_for('index'))
"""
