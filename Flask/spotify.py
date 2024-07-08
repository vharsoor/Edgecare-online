from flask import Flask, request, redirect, jsonify
import requests
import os
from flask_cors import CORS
import json
from config import public_ip

# Allow OAuthlib to use HTTP for local development
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set up Flask app
app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "*"}})


public_url = f'http://{public_ip}:4000'

#spotify creds
client_id_spotify = '3ce7a0b9ecb34103a13bd8ee5637a73f'
client_secret_spotify = '889ad9e4a1b244f183439951c4ae99d9'
redirect_url_spotify = f"{public_url}/spotify"

token_url = 'https://accounts.spotify.com/api/token'

@app.route('/api/spotify_auth', methods=['GET'])
def spotify_auth():
    
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id_spotify}"
        f"&redirect_uri={redirect_url_spotify}&scope=user-read-recently-played"
    )   

    return jsonify({'auth_url': auth_url})

#After user is redirected to redirect URL, directly use GET from backend to fetch the auth code
@app.route('/spotify', methods=['GET'])
def spotify_callback():
    code = request.args.get('code')

    token_params = {
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_url_spotify,
        'code': code
    }
    print("token_params : ",token_params)
    token_response = requests.post(token_url, data=token_params,auth=(client_id_spotify,client_secret_spotify))
    print(token_response)
    try:
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        user_data = fetch_spotify_data(access_token)
        if user_data:
            return jsonify(user_data)
        else:
            return 'Error fetching user data', 500
    except requests.exceptions.RequestException as e:
        return f'An error occurred: {e}', 500

def fetch_spotify_data(access_token):
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    recent_played_url = "https://api.spotify.com/v1/me/player/recently-played"
    response = requests.get(recent_played_url, headers=headers)
    user_data = response.json()

    #print("Top artists : ",user_data)
    return user_data

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=4000)
