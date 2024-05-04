import base64 
import requests 
from urllib.parse import urlencode
from flask import Blueprint, request, redirect, session, render_template

from src.config import Config

spotify_bp = Blueprint(
    name="spotify_bp",
    import_name=__name__,
    template_folder="templates",
)

@spotify_bp.route('/spotify-login')
def spotify_login():
    
    # Params 
    params = {
        'response_type': 'code',
        'client_id': Config.SPOTIFY_CLIENT_ID,
        'scope': Config.SCOPE,
        'redirect_uri': Config.REDIRECT_URI
    }

    return redirect(f"{Config.SPOTIFY_AUTH_URL}?{urlencode(params)}")


@spotify_bp.route('/callback')
def spotify_login_callback():
    
    # Access query params 
    code = request.args.get('code')

    # base64 encode client_id and client_secret
    request_string = Config.SPOTIFY_CLIENT_ID + ":" + Config.SPOTIFY_CLIENT_SECRET
    encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
    encoded_string = str(encoded_bytes, "utf-8")

    data = {
        'code': code,
        'redirect_uri': Config.REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    headers = {"Authorization": "Basic " + encoded_string}

    api_response = requests.post(
        Config.SPOTIFY_TOKEN_URL, 
        data=data,
        headers=headers 
    )

    api_response_data = api_response.json()
    access_token = api_response_data['access_token']

    headers = {
        "Authorization": f"Authorization: Bearer {access_token}"
    }

    # Fetch user profile data
    user_data_response = requests.get(
        f"{Config.SPOTIFY_BASE_URL}/me",
        headers=headers
    )

    user_data = user_data_response.json()

    session['user-name'] = user_data['display_name']
    session['user-email'] =  user_data['email']
    session['user-id'] =  user_data['id']
    session['user-profile'] = user_data['external_urls']['spotify']
    session['access-token'] = api_response_data['access_token']

    return redirect(f"{request.url_root}")


@spotify_bp.route('/spotify-logout')
def logout():
    session.clear()
    return redirect(f"{request.url_root}")