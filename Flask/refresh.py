import requests
import json
from datetime import datetime,timezone



#-----------------FACEBOOK------------------
client_id = '281055351768792'
client_secret = '12aae2a46d55fd214c04f856e5c39fd8'
public_url_fb = 'https://edgecare.stresswatch.net'
redirect_uri_fb = f"{public_url_fb}/callback"
token_url_fb = 'https://graph.facebook.com/v12.0/oauth/access_token'
fb_token_path='./fb_token.json'

def read_token_from_file(token_path):
    with open(token_path, 'r') as f:
        data = json.load(f)
    return data['access_token'],data['expires_in']


def store_token_to_file(token_path, access_token, expires_in):
    with open(token_path, 'w') as f:
        data = {
            'access_token': access_token,
            'expires_in': expires_in,
            'updated_at': datetime.now().isoformat()
        }
        json.dump(data, f)


def fb_exchange_token(client_id, client_secret, fb_token):
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'fb_exchange_token': fb_token
    }
    response = requests.get(token_url_fb, params=params)
    data = response.json()
    if 'access_token' in data:
        return data['access_token'], data.get('expires_in')
    else:
        raise Exception(f"Failed to exchange token: {data.get('error')}")

def facebook_refresh():
    try:
        # Read the current token from the file
        current_token, expires_in_days = read_token_from_file(fb_token_path)

        if expires_in_days<=15:
            # Exchange the current token for a new one
            new_token, expires_in_days = fb_exchange_token(client_id, client_secret, current_token)

            # Store the new token back to the file, if it expiration is close to 15 days
            store_token_to_file(fb_token_path, new_token, expires_in_days)

            print(f"FACEBOOK New token : {new_token}, expires in: {expires_in_days} days")
        else:
            print(f"FACEBOOK Old token works for {expires_in_days} days")

    except Exception as e:
        print(f"An error occurred: {e}")

#if __name__ == "__main__":
 #   main()


#-------------------------END--OF--FACEBOOK-----------------------------


#----------------------------GOOGLE-------------------------------------
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/chat.messages.readonly',
    'https://www.googleapis.com/auth/chat.messages',
    'https://www.googleapis.com/auth/chat.spaces',
    'https://www.googleapis.com/auth/chat.admin.spaces'
]

REDIRECT_URI = 'https://edgecare.stresswatch.net/api/exchange_code'
google_token_path = os.path.expanduser('./token.json')

def google_save_credentials(creds):
    with open(google_token_path, 'w') as token:
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
        json.dump(token_data, token)

def google_load_credentials(token_path):
    if os.path.exists(token_path):
        with open(token_path, 'r') as token_file:
            data = json.load(token_file)
            creds = Credentials(
                token=data['token'],
                refresh_token=data['refresh_token'],
                token_uri=data['token_uri'],
                client_id=data['client_id'],
                client_secret=data['client_secret'],
                scopes=data['scopes']
            )
            expiry = data.get('expiry')
            if expiry:
                expiry = datetime.fromisoformat(expiry).replace(tzinfo=timezone.utc)
            return creds, expiry

    return None, None

def is_token_expired(expiry_timestamp):
    if expiry_timestamp:
        now = datetime.now(timezone.utc)
        return expiry_timestamp < now
    return True

def google_refresh_credentials(creds):
    if creds and creds.refresh_token:
        creds.refresh(Request())
        print("GOOGLE credentials refreshed")
        google_save_credentials(creds)
        return creds
    return creds

def google_refresh():
    try:
        creds, expiry_timestamp = google_load_credentials(google_token_path)

        if creds is None or is_token_expired(expiry_timestamp):
            creds = google_refresh_credentials(creds)
        else:
            print("GOOGLE old credentials still alive")

        if not creds:
            print("No valid credentials found")

    except Exception as e:
        print(f"An error occurred: {e}")

#----------------END--OF--GOOGLE------------------------

#---------------------INSTAGRAM-------------------------

client_id_ig = '1126979348524869'
client_secret_ig = 'ad7609f32b6c9297517df0b1a907ccd1'
public_url = 'https://edgecare.stresswatch.net'

# OAuth endpoints
token_url_ig = 'https://api.instagram.com/oauth/access_token'
redirect_uri_ig = f"{public_url}/instagram"
long_lived_url_ig = 'https://graph.instagram.com/access_token'
ig_token_path = './ig_token.json'

def ig_exchange_token(client_id, client_secret, fb_token):
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': client_secret_ig,
        'access_token': access_token
    }
    response = requests.get(token_url_ig, params=params)
    data = response.json()
    if 'access_token' in data:
        return data['access_token'], data.get('expires_in')
    else:
        raise Exception(f"Failed to exchange token: {data.get('error')}")

def instagram_refresh():
    try:
        # Read the current token from the file
        current_token, expires_in_days = read_token_from_file(ig_token_path)

        if expires_in_days<=15:
            # Exchange the current token for a new one
            new_token, expires_in_days = ig_exchange_token(client_id, client_secret, current_token)

            # Store the new token back to the file, if it expiration is close to 15 days
            store_token_to_file(ig_token_path, new_token, expires_in_days)

            print(f"INSTAGRAM New token : {new_token}, expires in: {expires_in_days} days")
        else:
            print(f"INSTAGRAM Old token works for {expires_in_days} days")

    except Exception as e:
        print(f"An error occurred: {e}")

#----------------END--OF---INSTAGRAM----------------------

#---------------------SPOTIFY-----------------------------


#spotify creds
client_id_spotify = '3ce7a0b9ecb34103a13bd8ee5637a73f'
client_secret_spotify = '889ad9e4a1b244f183439951c4ae99d9'

token_url = 'https://accounts.spotify.com/api/token'

sp_token_path='./spotify_token.json'

# Function to read the token data from a file
def spotify_read_token_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

# Function to save the token data to a file
def spotify_save_token_data(filepath, token_data):
    with open(filepath, 'w') as file:
        json.dump(token_data, file)

# Function to get a new access token using the refresh token
def spotify_refresh_access_token(client_id, client_secret, refresh_token):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response_data.get('error_description', 'Unknown error')}")

    return response_data

def spotify_refresh():
    # Read the current token data
    token_data = spotify_read_token_data(sp_token_path)
    refresh_token = token_data.get('refresh_token')

    if not refresh_token:
        raise Exception("Refresh token not found in the token file.")

    # Get a new access token and refresh token
    try:
        new_token_data = spotify_refresh_access_token(
            client_id_spotify,
            client_secret_spotify,
            refresh_token
        )

        if 'refresh_token' not in new_token_data:
            new_token_data['refresh_token'] = refresh_token

        # Save the new token data
        spotify_save_token_data(sp_token_path, new_token_data)

        print("SPOFITY token refreshed ")
    except Exception as e:
        print(f"An error occurred: {e}")

#---------------------END--OF--SPOTIFY----------------------

if __name__ == "__main__":
    os.system('printf "refrest code ran" > test.py')
    google_refresh()
    facebook_refresh()
    instagram_refresh()
    spotify_refresh()
