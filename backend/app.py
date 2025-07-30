import os
import json
import time
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

#Initializing the flask application
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# Load environment variables
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
YOUTUBE_REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI')
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
                  'https://www.googleapis.com/auth/youtube.upload',
                  'https://www.googleapis.com/auth/youtube.force-ssl']
SPOTIFY_SCOPES = 'playlist-read-private playlist-modify-private user-library-read user-library-modify'
SPOTIFY_CACHE_FILE = '.spotify_cache.json'
YOUTUBE_CACHE_FILE = '.youtube_cache.json'
USERNAME = os.getenv('SPOTIFY_USERNAME')

# Creating and maintaining authenication tokens for spotify using SpotifyOAuth
def create_spotify():
    auth_manager = SpotifyOAuth(
        scope=SPOTIFY_SCOPES,
        username=USERNAME,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET)

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return auth_manager, spotify

# Function to refresh Spotify access token
def refresh_spotify(auth_manager, spotify):
    token_info = auth_manager.get_cached_token()
    # Create a new token if current is expired
    if auth_manager.is_token_expired(token_info):
        auth_manager, spotify = create_spotify()
    return auth_manager, spotify

# Spotify Authentication Routes

# Redirects user to the spotify login page
@app.route('/login')
def login():
    # Redirect to Spotify login page
    auth_manager, spotify = create_spotify()
    return redirect(auth_manager.get_authorize_url())

# On return from the spotify login page, store the auth token data for later use
@app.route('/callback')
def callback():
    auth_manager, spotify = create_spotify()
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)
    if token_info:
        # Check if 'refresh_token' is present
        if 'refresh_token' in token_info:
            store_spotify_credentials(token_info)  # Store Spotify credentials in cache
            return redirect('https://localhost:3000/transfer')
        else:
            return "Failed to retrieve refresh token from Spotify."
    else:
        return "Failed to retrieve access token from Spotify. Please try again."

# Retrive a user's spotify username
@app.route('/user-info')
def user_info():
    auth_manager, spotify = create_spotify()
    user_info = spotify.current_user()
    username = user_info['display_name']
    return jsonify({'username': username})

#Retrieve all public playlists on a spotify user's account
@app.route('/playlists')
def playlists():
    _, spotify = create_spotify()
    playlists = spotify.current_user_playlists()
    return jsonify({'playlists': playlists})

#  Youtube Authentication Routes

# Redirect user to the YouTube sign in page
@app.route('/authorize-youtube')
def authorize_youtube():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=YOUTUBE_SCOPES,
        redirect_uri=YOUTUBE_REDIRECT_URI)
    authorization_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(authorization_url)

# On return from the YouTube sign on page, store auth token data for future use
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=YOUTUBE_SCOPES,
        redirect_uri=YOUTUBE_REDIRECT_URI,
        state=state)
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Store YouTube credentials in cache
    store_youtube_credentials(credentials)

    return redirect('https://localhost:3000/transfer')

# Retrive a user's youtube username
@app.route('/youtube-user-info')
def youtube_user_info():
    credentials = load_youtube_credentials()
    if credentials:
        youtube = build('youtube', 'v3', credentials=credentials)
        channels_response = youtube.channels().list(
            part='snippet',
            mine=True
        ).execute()
        youtube_username = channels_response['items'][0]['snippet']['title']
        return jsonify({'youtubeusername': youtube_username})
    return jsonify({'youtubeusername': None})


# Helper functions for storing spotify credentials

# Store spotify auth credentials in a json file
def store_spotify_credentials(credentials):
    with open(SPOTIFY_CACHE_FILE, 'w') as f:
        json.dump(credentials, f)

# Retrieve the stored spotify credentials
def load_spotify_credentials():
    if os.path.exists(SPOTIFY_CACHE_FILE):
        with open(SPOTIFY_CACHE_FILE, 'r') as f:
            credentials = json.load(f)
            if credentials.get('expires_at') and datetime.fromtimestamp(credentials['expires_at']) > datetime.now():
                return credentials
    return None

# Helper functions for storing YouTube credentials

# Store YouTube auth credentials in a json file
def store_youtube_credentials(credentials):
    with open(YOUTUBE_CACHE_FILE, 'w') as f:
        json.dump(credentials_to_dict_youtube(credentials), f)

# Retrive the stored YouTube credentials
def load_youtube_credentials():
    if os.path.exists(YOUTUBE_CACHE_FILE):
        with open(YOUTUBE_CACHE_FILE, 'r') as f:
            return Credentials(**json.load(f))
    return None

# Format for storing the Youtube Credentials
def credentials_to_dict_youtube(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Functions for the playlist transfer functionality

MAX_RETRIES = 3  # Number of times program will retry if there is an error
RETRY_DELAY = 1  # Number of seconds between each retry

# Function to transfer playlist from Spotify to YouTube
def transfer_playlist(playlist_id, spotify):
    # Get playlist tracks
    playlist_tracks = spotify.playlist_tracks(playlist_id)

    # Initialize YouTube API
    youtube = build('youtube', 'v3', credentials=load_youtube_credentials())

    # Create a new YouTube playlist with the same name as Spotify playlist
    playlist_name = spotify.playlist(playlist_id)['name']
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name,
                "description": "This playlist was transferred from Spotify."
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    youtube_playlist_id = response['id']

    # Add tracks to YouTube playlist
    for track in playlist_tracks['items']:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        query = f"{track_name} {artist_name}"

        # Search for the track on YouTube
        search_request = youtube.search().list(
            part="snippet",
            q=query
        )
        search_response = search_request.execute()

        # If search returned results, add the first video to the playlist
        if search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            
            # Retry adding the video to the playlist in case of transient errors
            for attempt in range(MAX_RETRIES):
                try:
                    youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": youtube_playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    ).execute()
                    break  # Successfully added, exit loop
                except Exception as e:
                    print(f"Failed to add video (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        raise  # Retry limit reached, raise the exception

    return youtube_playlist_id

# Route to transfer playlist from Spotify to YouTube
@app.route('/transfer-playlist', methods=['POST'])
def transfer_playlist_route():
    data = request.json
    playlist_id = data.get('playlist_id')

    # Check if playlist_id is present
    if not playlist_id:
        return jsonify({'error': 'No playlist ID provided'}), 400

    # Create Spotify object
    auth_manager, spotify = create_spotify()

    # Transfer the playlist
    try:
        youtube_playlist_id = transfer_playlist(playlist_id, spotify)
        return jsonify({'youtube_playlist_id': youtube_playlist_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Functions for the song recommendation functionality

# Retrieve all songs in a spotify playlist
def get_playlist_tracks(playlist_id, spotify):
    playlist_tracks = spotify.playlist_tracks(playlist_id)
    tracks = []

    for track in playlist_tracks['items']:
        track_name = track['track']['name']
        track_id = track['track']['id']  # Get unique track ID
        tracks.append({'name': track_name, 'id': track_id})

    return tracks

# Get the recommendations from the tracks using the get_playlist_tracks function
def get_recommendations_from_playlist(playlist_id, spotify):
    # Get tracks from the playlist
    playlist_tracks = get_playlist_tracks(playlist_id, spotify)
    track_ids = [track['id'] for track in playlist_tracks]  # Extract track IDs

    # Get recommendations excluding tracks from the playlist
    recommendations = []
    for track_id in track_ids:
        # Get recommendations for each track
        results = spotify.recommendations(seed_tracks=[track_id], limit=5)
        for result in results['tracks']:
            # Check if the recommended track is not in the playlist
            if result['id'] not in track_ids:
                recommendations.append(result['name'] + ' by ' + result['artists'][0]['name'])

    # Return unique recommendations
    return list(set(recommendations))[:10]

# Route to use in order to get the recommendations to the front-end
@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    playlist_id = data.get('playlist_id')

    # Check if playlist_id is present
    if not playlist_id:
        return jsonify({'error': 'No playlist ID provided'}), 400

    # Create Spotify object
    auth_manager, spotify = create_spotify()

    # Get recommendations for the playlist
    try:
        recommendations = get_recommendations_from_playlist(playlist_id, spotify)
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run python app and use SSL to enable HTTPS
if __name__ == '__main__':
    app.run(debug=True, ssl_context=('../cert.pem', '../key.pem'))