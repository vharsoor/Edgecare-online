from flask import Flask, request, redirect, jsonify
import requests
import os
import urllib.parse
from flask_cors import CORS

# Allow OAuthlib to use HTTP for local development
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set up Flask app
app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# OAuth endpoints
authorization_base_url = 'https://www.facebook.com/v12.0/dialog/oauth'
token_url = 'https://graph.facebook.com/v12.0/oauth/access_token'

@app.route('/api/facebook_auth', methods=['POST'])
def facebook_auth():
    data = request.json
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    public_url = data.get('public_url')

    # Save the credentials securely if needed
    app.config['CLIENT_ID'] = client_id
    app.config['CLIENT_SECRET'] = client_secret
    app.config['PUBLIC_URL'] = public_url

    redirect_uri = f"{public_url}/callback"
    auth_url = (
        f"https://www.facebook.com/v12.0/dialog/oauth?client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope=user_likes,user_posts"
    )

    return jsonify({'auth_url': auth_url})

@app.route('/callback', methods=['GET'])
def callback():
    #if 'CLIENT_ID' not in app.config or 'CLIENT_SECRET' not in app.config or 'PUBLIC_URL' not in app.config:
        #return "Error: Missing configuration values. Ensure you have set CLIENT_ID, CLIENT_SECRET, and PUBLIC_URL via /api/facebook_auth endpoint.", 400
    
    print("Entering callback")
    code = request.args.get('code')
    client_id = app.config['CLIENT_ID']
    client_secret = app.config['CLIENT_SECRET']
    redirect_uri = f"{app.config['PUBLIC_URL']}/callback"

    token_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'client_secret': client_secret,
        'code': code
    }
    print("token_params : ",token_params)
    token_response = requests.get(token_url, params=token_params)

    try:
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        long_lived_token_response = exchange_access_token(access_token)
        long_lived_token = long_lived_token_response.get('access_token')

        user_data = fetch_user_data(long_lived_token)
        if user_data:
            print(jsonify(user_data))
            return jsonify(user_data)
        else:
            return 'Error fetching user data', 500
    except requests.exceptions.RequestException as e:
        return f'An error occurred: {e}', 500

def exchange_access_token(access_token):
    url = "https://graph.facebook.com/v12.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app.config['CLIENT_ID'],
        'client_secret': app.config['CLIENT_SECRET'],
        'fb_exchange_token': access_token
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_all_data(url, params):
    data = []
    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_response = response.json()
        if 'data' in json_response:
            data.extend(json_response['data'])
        if 'paging' in json_response and 'next' in json_response['paging']:
            url = json_response['paging']['next']
            params = None
        else:
            break
    return data

def fetch_user_data(access_token):
    user_info_url = 'https://graph.facebook.com/me'
    user_fields = 'id,name,birthday,friends,posts{source,full_picture,updated_time,status_type}'

    params = {
        'access_token': access_token,
        'fields': user_fields
    }

    try:
        user_info_response = requests.get(user_info_url, params=params)
        user_info_response.raise_for_status()

        user_info = user_info_response.json()

        if 'friends' in user_info:
            friends_data = fetch_all_data('https://graph.facebook.com/me/friends', {
                'access_token': access_token
            })
            user_info['friends']['data'] = friends_data

        if 'posts' in user_info:
            posts_data = fetch_all_data('https://graph.facebook.com/me/posts', {
                'access_token': access_token,
                'fields': 'source,full_picture,updated_time,status_type'
            })
            user_info['posts']['data'] = posts_data

        return {'userInfo': user_info}
    except requests.exceptions.RequestException as e:
        return None

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
