from app import db
from datetime import datetime

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(100), nullable=False)
    hobbies = db.Column(db.Text)
    characteristics = db.Column(db.Text)
    genre = db.Column(db.String(50))  # New field for music genre
    lyrics = db.Column(db.Text)
    audio_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default='pending')
    stripe_payment_id = db.Column(db.String(100))
