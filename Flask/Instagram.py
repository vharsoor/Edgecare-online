from flask import Flask, request, redirect, jsonify
import requests
import os
import urllib.parse
from flask_cors import CORS

# Allow OAuthlib to use HTTP for local development
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

client_id_ig = '1126979348524869'
client_secret_ig = 'ad7609f32b6c9297517df0b1a907ccd1'
public_url = 'https://edgecare.stresswatch.net'

# Set up Flask app
app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# OAuth endpoints
token_url_ig = 'https://api.instagram.com/oauth/access_token'
redirect_uri_ig = f"{public_url}/instagram"
long_lived_url_ig = 'https://graph.instagram.com/access_token'

@app.route('/api/instagram_auth', methods=['GET'])
def facebook_auth():
    #data = request.json
    #client_id = data.get('client_id')
    #client_secret = data.get('client_secret')
    #public_url = data.get('public_url')

    # Save the credentials securely if needed
    app.config['CLIENT_ID'] = client_id_ig
    app.config['CLIENT_SECRET'] = client_secret_ig
    app.config['PUBLIC_URL'] = public_url

    auth_url = (
        f"https://api.instagram.com/oauth/authorize?client_id={client_id_ig}"
        f"&redirect_uri={redirect_uri_ig}&scope=user_media,user_profile&response_type=code"
    )

    return jsonify({'auth_url': auth_url})

@app.route('/instagram', methods=['GET'])
def callback():

    print("Entering callback")
    code = request.args.get('code')

    token_params = {
        'client_id': client_id_ig,
        'client_secret': client_secret_ig,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri_ig,
        'code': code
    }
    print("token_params : ",token_params)
    token_response = requests.post(token_url_ig, data=token_params)
    print("Got token reponse :",token_response)
    try:
        token_response.raise_for_status()
        print("Try for access_token")
        access_token = token_response.json().get('access_token')
        print("access_token : ",access_token)
        long_lived_token_response_ig = exchange_access_token_ig(access_token)
        long_lived_token_ig = long_lived_token_response_ig.get('access_token')

        #user_data = fetch_user_data(long_lived_token)
        user_data = fetch_user_data(long_lived_token_ig)
        if user_data:
            print(jsonify(user_data))
            return jsonify(user_data)
        else:
            return 'Error fetching user data', 500
    except requests.exceptions.RequestException as e:
        return f'An error occurred: {e}', 500

def exchange_access_token_ig(access_token):
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': client_secret_ig,
        'access_token': access_token
    }
    response = requests.get(long_lived_url_ig, params=params)
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
    user_info_url = 'https://graph.instagram.com/me/media'
    user_fields = 'id,caption,media_type,media_url,permalink,timestamp,username'

    params = {
        'access_token': access_token,
        'fields': user_fields
    }

    try:
        print("before fetching data")
        
        #user_info_response = requests.get(user_info_url, params=params)
        #user_info_response.raise_for_status()

        #user_info = user_info_response.json()
        user_info = fetch_all_data(user_info_url,params)

        return {'userInfo': user_info}
    except requests.exceptions.RequestException as e:
        return None

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=4000)
