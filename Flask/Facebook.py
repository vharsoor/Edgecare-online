from flask import Flask, request, redirect
import requests
import os
import urllib.parse

# Allow OAuthlib to use HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set up Flask app
app = Flask(__name__)

# Facebook app credentials
client_id = '281055351768792'
client_secret = '12aae2a46d55fd214c04f856e5c39fd8'
public_url = 'http://localhost:5000'

# Redirect URI
redirect_uri = '{}/auth/facebook/callback'.format(public_url)
print('Redirect URI: {}'.format(redirect_uri))

# OAuth endpoints
authorization_base_url = 'https://www.facebook.com/v12.0/dialog/oauth'
token_url = 'https://graph.facebook.com/v12.0/oauth/access_token'

@app.route("/")
def index():
    print("trial 0")
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'user_likes,user_posts',
        'response_type': 'code'  # Ensure this is included
    }
    print("trial1")
    authorization_url = '{}?{}'.format(authorization_base_url, urllib.parse.urlencode(auth_params))
    print('Authorization URL: {}'.format(authorization_url))
    return redirect(authorization_url)

@app.route("/auth/facebook/callback")
def callback():
    print('Received callback with URL: {}'.format(request.url))
    code = request.args.get('code')
    if not code:
        return "Error: No code provided in callback URL", 400
    
    print("Authorization code: {}".format(code))
    
    token_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'client_secret': client_secret,
        'code': code
    }
    
    token_response = requests.get(token_url, params=token_params)
    print("Token response: {}".format(token_response))
    
    try:
        token_response.raise_for_status()  # Raise an exception for HTTP errors
        token = token_response.json().get('access_token')
        print("Access token: {}".format(token))
        
        long_lived_token_response = exchange_access_token(token)
        long_lived_token = long_lived_token_response.get('access_token')
        
        user_data = fetch_user_data(long_lived_token)
        if user_data:
            print('User Info:')
            print(user_data['userInfo'])
            return user_data['userInfo']
        else:
            return 'Error fetching user data', 500
    except requests.exceptions.RequestException as e:
        print('Error: {}'.format(e))
        return 'An error occurred: {}'.format(e), 500

def exchange_access_token(access_token):
    url = "https://graph.facebook.com/v12.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': client_id,
        'client_secret': client_secret,
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
            params = None  # After the first page, params should be None because 'next' already includes the access token
        else:
            break
    return data

def fetch_user_data(access_token):
    user_info_url = 'https://graph.facebook.com/me'

    # Define the fields you want to fetch
    user_fields = 'id,name,birthday,friends,posts{source,full_picture,updated_time,status_type}'

    params = {
        'access_token': access_token,
        'fields': user_fields
    }

    try:
        # Fetch user info with the specified fields
        user_info_response = requests.get(user_info_url, params=params)
        user_info_response.raise_for_status()  # Raise an exception for HTTP errors

        user_info = user_info_response.json()

        # Handle pagination for friends and posts
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

        print("user_info : ",user_info)
        return {
            'userInfo': user_info,
        }

    except requests.exceptions.RequestException as e:
        print('Error fetching user data: {}'.format(e))
        return None


