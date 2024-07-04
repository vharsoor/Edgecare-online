from flask import Flask, request, redirect, jsonify
import requests
import os
from flask_cors import CORS
import json

# Allow OAuthlib to use HTTP for local development
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set up Flask app
app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# OAuth endpoints
#authorization_base_url = 'https://discord.com/oauth2/authorize'
token_url = 'https://accounts.spotify.com/api/token'
public_url = 'http://localhost:5000'

@app.route('/api/discord_auth', methods=['POST'])
def facebook_auth():
    data = request.json
    #client_id = data.get('client_id')
    client_id = '3ce7a0b9ecb34103a13bd8ee5637a73f'
    #client_secret = data.get('client_secret')
    client_secret = '889ad9e4a1b244f183439951c4ae99d9'
    #public_url = data.get('public_url')
    public_url = 'http://localhost:5000'

    # Save the credentials securely if needed
    app.config['CLIENT_ID'] = client_id
    app.config['CLIENT_SECRET'] = client_secret
    app.config['PUBLIC_URL'] = public_url

    redirect_uri = f"{public_url}/spotify"
    auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope=me"
    )   

    return jsonify({'auth_url': auth_url})

@app.route('/spotify', methods=['GET'])
def callback():
    #if 'CLIENT_ID' not in app.config or 'CLIENT_SECRET' not in app.config or 'PUBLIC_URL' not in app.config:
        #return "Error: Missing configuration values. Ensure you have set CLIENT_ID, CLIENT_SECRET, and PUBLIC_URL via /api/facebook_auth endpoint.", 400

    print("Entering callback")
    code = request.args.get('code')
    #client_id = app.config['CLIENT_ID']
    client_id = '3ce7a0b9ecb34103a13bd8ee5637a73f'
    #client_secret = app.config['CLIENT_SECRET']
    client_secret = '889ad9e4a1b244f183439951c4ae99d9'
    #redirect_uri = f"{app.config['PUBLIC_URL']}/discord"
    redirect_uri = f"{public_url}/spotify"

    token_params = {
        'grant_type': 'authorization_code',
        #'client_id': client_id,
        'redirect_uri': redirect_uri,
        #'client_secret': client_secret,
        'code': code
    }
    print("token_params : ",token_params)
    token_response = requests.post(token_url, data=token_params,auth=(client_id,client_secret))
    print(token_response)
    try:
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')
        print("access_token fulll : ",access_token)

        #long_lived_token_response = exchange_access_token(access_token)
        #long_lived_token = long_lived_token_response.get('access_token')
        print("Lets use access_token")
        user_data = fetch_user_data(access_token)
        if user_data:
            print("We have some user data")
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
    headers = {
    'Authorization': f'Bearer {access_token}'
}

    # Fetch the user's information
    '''user_url = "https://api.spotify.com/v1/me"
    response = requests.get(user_url, headers=headers)
    user_data = response.json()

    print("Spotify User info : ",user_data)'''

    user_url = "https://api.spotify.com/v1/me/player/recently-played"
    response = requests.get(user_url, headers=headers)
    user_data = response.json()

    print("Top artists : ",user_data)
    return user_data

    # Fetch the user's guilds
    '''guilds_url = "https://discord.com/api/v10/users/@me/guilds"
    response = requests.get(guilds_url, headers=headers)
    guilds_data = response.json()

    print("guilds data : ",guilds_data)

    conn_url = "https://discord.com/api/v10/users/@me/connections"
    response = requests.get(conn_url, headers=headers)
    conn_data = response.json()

    print("conn data : ",conn_data)

    guild_ids=[]
    for guild in guilds_data:
        guild_ids.append(guild['id'])
    
    
    guild_mem_data=[]
    for guild_id in guild_ids:
        guild_url = f"https://discord.com/api/v10/users/@me/guilds/{guild_id}/member"
        guild_id_url = guild_url.format(guild_id=guild_id)
        guild_mem_data.append(requests.get(guild_id_url, headers=headers).json())
    
    print("guild_mem_data data : ",guild_mem_data)

    # Replace with your bot token
    

    # Set the headers with the bot token
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    for gc in guilds_data:
        guild_id = gc['id']
        #channel_id = gc['channel_id']
        
        # Fetch guild channels
        channels_url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
        response = requests.get(channels_url, headers=headers)
        channels_data = response.json()
        print(f"Channels in Guild {guild_id}:")
        print(channels_data)'''
        
        # Fetch messages from a specific channel
    '''channel_id = '847719473971986486'
    messages_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    response = requests.get(messages_url, headers=headers)
    messages_data = response.json()
    print(f"Messages in Channel {channel_id}:")
    #print(json.dumps(messages_data))
    for message in messages_data:
    # Process each message object in the list here
        print(message)  # Example: print message details'''
        

if __name__ == '__main__':
    app.run(debug=True)#,host='0.0.0.0')