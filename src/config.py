import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SPOTIFY
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = f"http://34.28.219.91:8000/callback"
    SCOPE = "user-read-private user-read-email playlist-modify-private"
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
    

    # OPENAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_GPT_MODEL = "gpt-4-0125-preview"
    RESPONSE_TIME_LIMIT = 3600


    # FLASK
    HOST = "0.0.0.0"
    PORT = 8000
    FLASK_BASE_URL = "http://localhost:8000"
    FLASK_SESSION_SECRET_KEY = os.environ.get('FLASK_SESSION_SECRET_KEY')
