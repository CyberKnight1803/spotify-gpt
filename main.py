import json
from flask import Flask, render_template, session, request

from src.spotify_auth import spotify_bp
from src.suggestions import suggestions_bp
from src.config import Config

# app
app = Flask(__name__)
app.secret_key = Config.FLASK_SESSION_SECRET_KEY

# routes 
app.register_blueprint(spotify_bp)
app.register_blueprint(suggestions_bp)

@app.route('/')
def home_page():
    messages = request.args.get('messages', None)

    if messages is not None:
        messages = json.loads(messages)

    if 'user-name' in session:
        user_details = {}
        user_details['user-name'] = session['user-name']
        user_details['user-email'] = session['user-email']
        user_details['user-profile'] = session['user-profile']
        user_details['access-token'] = session['access-token']
    
    else:
        user_details = None

    if 'suggested_tracks' in session:
        suggested_tracks = session['suggested_tracks']
    
    else:
        suggested_tracks = None
    
    if 'playlist_link' in session:
        playlist_name = session['playlist_name']
        playlist_link = session['playlist_link']
    
    else: 
        playlist_link = None
        playlist_name = None

    return render_template(
        'home.html', 
        login_url=f"{request.base_url}/spotify-login", 
        logout_url=f"{request.base_url}/spotify-logout",
        user_details=user_details, 
        messages=messages,
        suggested_tracks=suggested_tracks, 
        playlist_link=playlist_link,
        playlist_name=playlist_name
    )




if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=True
    )