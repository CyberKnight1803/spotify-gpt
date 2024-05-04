import json
from openai import OpenAI
import requests
from urllib.parse import urlencode
from flask import Blueprint, session, redirect, url_for, request
from src.config import Config

suggestions_bp = Blueprint(
    'suggestions', 
    __name__
)

openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)


@suggestions_bp.route('/suggest', methods=['POST'])
def suggest():

    if 'user-name' not in session:
        messages = json.dumps({'error': 'Please login to get suggestions.'})
        return redirect(url_for('home_page', messages=messages))

    user_prompt = request.form.get('user_prompt', None)
    num_songs = request.form.get('num_songs', None)

    if user_prompt is None or num_songs is None:
        messages = json.dumps({'error': 'Please enter a prompt and number of songs to get suggestions!'})
        return redirect(url_for('home_page', messages=messages))

    system_prompt = f"""
    You are the best Spotify song recommender this world has ever seen. 
    You accurately understand the user's feelings and desire to hear the type of songs from his request and you suggest the best songs which could be turned into the best playlist.
    You only recommend songs available on spotify.
    """ 


    # Prompt to get suggestions
    prompt = f"""
    Suggest {num_songs} songs based on the following user's prompt: 

    {user_prompt}

    Note: Follow the below rules strictly to generate the output
    1. You are to suggest only track names and first artist 
    2. The output should strictly be JSON parsable. 

    Example: Output for 2 songs recommended by you should look like a list of 2 dictionaries, where each dictionary will have two key value pairs i.e. "title": "song_name", "artist": "artist_name"
    """

    # Get reponse from gpt-4
    response = openai_client.chat.completions.create(
        model=Config.OPENAI_GPT_MODEL, 
        max_tokens=2000,
        response_format={
            'type': 'json_object'           # GPT-4 Turbo model can set JSON object as output format
        },
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # Get dictionary format
    songs = json.loads(response.choices[0].message.content)['songs']

    suggested_tracks = []
    for song in songs:
        params = {
            'q': f"{song['title']}%{song['artist']}",
            'type': 'track',
            'limit': 1
        }

        headers = {
            "Authorization": f"Authorization: Bearer {session['access-token']}"
        }

        response = requests.get(
            f"{Config.SPOTIFY_BASE_URL}/search?{urlencode(params)}",
            headers=headers
        )

        # Process artists 
        track_details = response.json()

        try:
            artists = []
            for artist in track_details['tracks']['items'][0]['artists']:
                artists.append(artist['name'])

            track_data = {
                "id": track_details['tracks']['items'][0]['id'], 
                "name": track_details['tracks']['items'][0]['name'],
                "artists": artists,
                'external_url': track_details['tracks']['items'][0]['external_urls']['spotify'], 
                'images': track_details['tracks']['items'][0]['album']['images']
            }

            suggested_tracks.append(track_data)
            session['suggested_tracks'] = suggested_tracks
        except:
            print(track_details)

    return redirect(f"{request.url_root}")

@suggestions_bp.route('/add-to-playlist', methods=['POST'])
def add_to_playlist():
    playlist_name = request.form.get('playlist_name', None)
    track_ids = request.form.getlist('track_ids[]', None)

    data = {
        'name': playlist_name,
        'public': False
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Authorization: Bearer {session['access-token']}"
    }

    response = requests.post(
        f"{Config.SPOTIFY_BASE_URL}/users/{session['user-id']}/playlists",
        data=json.dumps(data),
        headers=headers
    )

    playlist_details = response.json()
    playlist_id = playlist_details['id']
    playlist_link = playlist_details['external_urls']['spotify']
    
    uris = []
    for track_id in track_ids:
        uris.append(f"spotify:track:{track_id}")
    
    data = {
        'uris': uris
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Authorization: Bearer {session['access-token']}"
    }

    snapshot_id = requests.post(
        f"{Config.SPOTIFY_BASE_URL}/playlists/{playlist_id}/tracks",
        data=json.dumps(data),
        headers=headers
    )

    session.pop('suggested_tracks', None)
    session['playlist_link'] = playlist_link
    session['playlist_name'] = playlist_name

    return redirect(f"{request.url_root}")