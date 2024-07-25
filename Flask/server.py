from flask import Flask, request, jsonify, redirect
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import urllib.error
import datetime
from flask_cors import CORS
from config import public_ip
import json
import zipfile
import shutil
from flask import send_file
import praw
import requests

from flask import Flask, session
from flask_session import Session

app = Flask(__name__)
# CORS(app)

cors = CORS(app, resources={r"/*": {"origins": "http://34.207.174.211:3000", "supports_credentials": True}})

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'
app.secret_key = 'supersecretkey'

Session(app)
#----------------------Login Page-------------------------
# Hardcoded credentials 
HARDCODED_USERS = {
    'edgecare1': 'visa1',
    'edgecare2': 'visa2',
    'edgecare3': 'visa3',
    'edgecare4': 'visa4',
    'edgecare5': 'visa5',
}

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print("username : ",username, " password : ",password)
    # global current_user
    # current_user = {'username': username, 'password': password}

    session['username'] = username

    if username in HARDCODED_USERS and HARDCODED_USERS[username] == password:
        session.permanent = True
        print(f"Session data: {session}")  
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# @app.route('/current_user', methods=['GET'])
# def get_current_user():
#     return jsonify(current_user)
@app.route('/current_user', methods=['GET'])
def get_current_user():
    print("Session data:", session)
    if 'username' in session:
        username = session['username']
        return jsonify({'username': username}), 200
    else:
        return jsonify({'message': 'No user logged in'}), 401


#---------------------------------------------------------



#----------------GOOGLE--PLATFORMS------------------------

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

def get_credentials(credentials_path):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

#Frontend fetches the auth URL from backend, which creates the URL using our app creds
@app.route('/api/google_auth', methods=['GET'])
def api_get_credentials():
    credentials_path = os.path.expanduser('./google_creds.json')
    
    # Ensure the credentials file exists
    if not os.path.exists(credentials_path):
        return jsonify({'message': 'Credentials file not found'}), 404
    
    # Get the authentication URL
    auth_url = get_credentials(credentials_path)
    print("auth_url : ",auth_url)
    return jsonify({'auth_url': auth_url}), 200

#Get request as backend directly fethes auth code from the redirected URL
@app.route('/api/exchange_code', methods=['GET'])
def exchange_code():
    code = request.args.get('code')
    #credentials_path = request.json.get('credentials_path')
    credentials_path = os.path.expanduser('./google_creds.json')
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    
    creds = flow.credentials
    app.config['creds'] = creds
    
    calendar = api_fetch_calendar_events().get_json()
    gmail = api_gmail_collect().get_json()
    #chat = api_fetch_chat_messages().get_json()
    print("calendar type :", type(calendar))
    #google = {**calendar,**gmail}
    google = calendar + gmail 
    return jsonify(google)

#@app.route('/api/gmail_collect')
def api_gmail_collect():
    emails = gmail_collect(app.config['creds'])
    return jsonify(emails)#, 200

def api_fetch_calendar_events():
    events = fetch_calendar_events(app.config['creds'])
    return jsonify(events)#, 200

def api_fetch_chat_messages():
    chat_messages = get_chat_messages(app.config['creds'])
    return jsonify(chat_messages)

def gmail_collect(creds):
    service = build('gmail', 'v1', credentials=creds)
    received_messages = get_messages(service, 'me', query='in:inbox')
    sent_messages = get_messages(service, 'me', query='in:sent')

    received_emails = []
    for msg in received_messages[:10]:
        details = get_message_details(service, 'me', msg['id'])
        if details:
            received_emails.append(details)

    sent_emails = []
    for msg in sent_messages[:10]:
        details = get_message_details(service, 'me', msg['id'])
        if details:
            sent_emails.append(details)

    #return {'received_emails': received_emails, 'sent_emails': sent_emails}
    return [received_emails,sent_emails]

def fetch_calendar_events(creds):
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    one_year_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=one_year_ago,
                                          timeMax=now, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    calendar_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date')) if event['end'] else None
        calendar_events.append({
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', 'No Description'),
            'location': event.get('location', 'No Location'),
            'start': start,
            'end': end,
            'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
            'organizer': event['organizer'].get('email', 'No Organizer'),
            'creator': event.get('creator').get('email', 'No Creator'),
            'recurrence': event.get('recurrence', 'No Recurrence'),
            'reminders': event.get('reminders', {}).get('useDefault', 'No Reminders'),
            'status': event.get('status', 'No Status'),
            'visibility': event.get('visibility', 'No Visibility'),
            'colorId': event.get('colorId', 'No Color ID'),
            'hangoutLink': event.get('hangoutLink', 'No Hangout Link')
        })

    return calendar_events

def get_messages(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except urllib.error.HTTPError as error:
        print(f'An error occurred: {error}')
        return []

def get_message_details(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        headers = message['payload']['headers']
        subject = ''
        date = ''
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'Date':
                date = header['value']
        snippet = message['snippet']
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        return {'subject': subject, 'date': date, 'snippet': snippet, 'body': body}
    except urllib.error.HTTPError as error:
        print(f'An error occurred: {error}')
        return None

#--------------------------------------------------------------------------------------

# def get_credentials():
#     creds = None
    
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 r'C:\Users\USER\Desktop\Edgecare\edgecare\Flask\client_secret_382500969024-ptpt03tjh99bcu2jga9o0htai1pieiqs.apps.googleusercontent.com.json', SCOPES, redirect_uri="http://127.0.0.1:5000")
#             creds = flow.run_local_server(port=5000)
        
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
    
#     return creds

def list_spaces(service):
    # space means the chat group room or direct private messages
    spaces = service.spaces().list().execute().get('spaces', [])
    space_list = []
    for space in spaces:
        if 'displayName' in space:
            space_list.append({'name': space['name'], 'displayName': space['displayName']})
        else:
            space_list.append({'name': space['name'], 'displayName': space['name']})
    return space_list

def list_messages(service, space_name):
    # list all the content 
    message_list = []
    page_token = None
    
    while True:
        if page_token:
            response = service.spaces().messages().list(parent=space_name, pageToken=page_token).execute()
        else:
            response = service.spaces().messages().list(parent=space_name).execute()
        
        messages = response.get('messages', [])
        for message in messages:
            message_text = message.get('text', 'No text content')
            message_list.append(message_text)
        
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return message_list

def get_chat_messages(creds):
    
    service = build('chat', 'v1', credentials=creds)

    spaces = list_spaces(service)
    
    # if messages list lower than 2
    num_spaces = min(len(spaces), 2)
    chat_messages = {}

    for i in range(num_spaces):
        space = spaces[i]
        messages = list_messages(service, space['name'])
        chat_messages[space['displayName']] = messages

    return jsonify(chat_messages)

#---------END--OF--GOOGLE--PLATFORMS---------------

#-------------------FACEBOOK-----------------------

client_id = '281055351768792'
client_secret = '12aae2a46d55fd214c04f856e5c39fd8'
public_url_fb = 'https://edgecare.stresswatch.net'
redirect_uri_fb = f"{public_url_fb}/callback"

authorization_base_url = 'https://www.facebook.com/v12.0/dialog/oauth'
token_url_fb = 'https://graph.facebook.com/v12.0/oauth/access_token'


@app.route('/api/facebook_auth', methods=['GET'])
def facebook_auth():
    #data = request.json
    #client_id = data.get('client_id')
    #client_secret = data.get('client_secret')
    #public_url = data.get('public_url')

    # Save the credentials securely if needed
    app.config['CLIENT_ID'] = client_id
    app.config['CLIENT_SECRET'] = client_secret
    app.config['PUBLIC_URL'] = public_url

    redirect_uri_fb = f"{public_url_fb}/callback"
    auth_url = (
        f"https://www.facebook.com/v12.0/dialog/oauth?client_id={client_id}"
        f"&redirect_uri={redirect_uri_fb}&scope=user_likes,user_posts"
    )

    return jsonify({'auth_url': auth_url})

@app.route('/callback', methods=['GET'])
def callback():

    print("Entering callback")
    code = request.args.get('code')
    client_id = app.config['CLIENT_ID']
    client_secret = app.config['CLIENT_SECRET']
    redirect_uri = f"{app.config['PUBLIC_URL']}/callback"

    token_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri_fb,
        'client_secret': client_secret,
        'code': code
    }
    print("token_params : ",token_params)
    token_response = requests.get(token_url_fb, params=token_params)

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

#--------------END--OF--FACEBOOK--------------------

#------------------REDDIT---------------------------

# @app.route('/api/reddit', methods=['POST'])
# def receive_reddit_id():
#     data = request.get_json()
#     reddit_id = data.get('reddit_id')
#     print(f"Received Reddit User ID: {reddit_id}")

        
#     # Reddit credential secret
#     CLIENT_ID = 'vDlSP0b2Loia3loPC1ObsQ'
#     CLIENT_SECRET = '6fGr2o1BqgMdAdTWePHLSJwozfimyw'
#     USER_AGENT = 'RedditPostFetcher/1.0 by Warm-Cucumber-3293'

#     # target user name
#     TARGET_USER = str(reddit_id)
#     # ex. ARGET_USER = 'Warm-Cucumber-3293'

#     # to store all the list and content of the user
#     user_all_data = []


#     reddit = praw.Reddit(
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         user_agent=USER_AGENT
#     )

    
#     user = reddit.redditor(TARGET_USER)
#     posts = user.submissions.new(limit=None)

    
#     user_folder = os.path.join('content', TARGET_USER)
#     os.makedirs(user_folder, exist_ok=True)

   
#     for post in posts:

#         user_database = {
#             "Type": "Post",
#             "Title": post.title,
#             "Subreddit": str(post.subreddit),
#             "URL": post.url,
#             "Score": post.score,
#             "Upvote Ratio": post.upvote_ratio,
#             "Comments": post.num_comments,
#             "Unix timestamp Created at": post.created_utc,
#             "Created at": datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
#             "Post ID": post.id,
#             "Text-based Content": post.selftext if post.is_self else None,
#             "Image Content URL": post.url if not post.is_self else None
#         }

    
        
#         if post.is_self:
            
#             print(f"Text-based Content: {post.selftext}")
#         else:
            
#             print(f"Image Content URL: {post.url}")

#             image_url = post.url
#             file_extension = os.path.splitext(image_url)[1]

#             if not file_extension:
                
#                 file_extension = '.jpg'
    

            
#             try:
#                 response = requests.get(image_url)
#                 if response.status_code == 200:
#                     image_data = response.content
#                     # image_filename = os.path.join('content/', f'{post.id}.jpg')
#                     # image_filename = os.path.join('content', f'{post.id}{file_extension}')
#                     image_filename = os.path.join(user_folder, f'{post.id}{file_extension}')
#                     with open(image_filename, 'wb') as image_file:
#                         image_file.write(image_data)
#                     print(f"Image downloaded successfully: {image_filename}, saved to {image_filename}")
#                 else:
#                     print(f"Failed to download image: {image_url}")
#             except Exception as e:
#                 print(f"Error downloading image: {e}")
            
#         print("=" * 40)
#         user_all_data.append(user_database)


    
#     user = reddit.redditor(TARGET_USER)
#     comments = user.comments.new(limit=None)

    
#     for comment in comments:

#         comment_database = {
#             "Type": "Comment",
#             "Subreddit": str(comment.subreddit),
#             "Score": comment.score,
#             "Unix timestamp Created at": comment.created_utc,
#             "Created at": datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
#             "Comment ID": comment.id,
#             "Parent ID": comment.parent_id,
#             "Content": comment.body
#         }


#         # print(f"Subreddit: {comment.subreddit}")
#         # print(f"Score: {comment.score}")
#         # print(f"Unix timestamp Created at: {comment.created_utc}")
#         # created_at = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
#         # print(f"Created at: {created_at}")
#         # print(f"Comment ID: {comment.id}")
#         # print(f"Parent ID: {comment.parent_id}")
#         # print(f"Content: {comment.body}")
#         # print("*" * 40)

#         user_all_data.append(comment_database)



#     print(user_all_data)

    
#     output_file = os.path.join(user_folder, 'user_data.json')
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(user_all_data, f, ensure_ascii=False, indent=4)

#     print(f"All posts data saved to {output_file}")

#     shutil.make_archive(user_folder, 'zip', user_folder)
#     zip_filename = f'{reddit_id}.zip'
#     print("--")
#     print(zip_filename)
#     print(f'{user_folder}.zip')
#     print("--")

#     return send_file(f'{user_folder}.zip', as_attachment=True, download_name=zip_filename)
#     # return jsonify({'message': 'Received Reddit User ID successfully'})

import mysql.connector

# MySQL connection configuration
db_config = {
    'user': 'root',
    'password': '19991211',
    'host': 'localhost',
    'database': 'reddit_data'
}

@app.route('/api/reddit', methods=['POST'])
def receive_reddit_id():
    data = request.get_json()
    reddit_id = data.get('reddit_id')
    print(f"Received Reddit User ID: {reddit_id}")

    CLIENT_ID = 'vDlSP0b2Loia3loPC1ObsQ'
    CLIENT_SECRET = '6fGr2o1BqgMdAdTWePHLSJwozfimyw'
    USER_AGENT = 'RedditPostFetcher/1.0 by Warm-Cucumber-3293'
    TARGET_USER = str(reddit_id)
    user_all_data = []

    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    user = reddit.redditor(TARGET_USER)
    posts = user.submissions.new(limit=None)

    for post in posts:
        post_data = (
            "Post",
            post.title,
            str(post.subreddit),
            post.url,
            post.score,
            post.upvote_ratio,
            post.num_comments,
            datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            post.id,
            post.selftext if post.is_self else None,
            post.url if not post.is_self else None,
            None  # Placeholder for image_content
        )
        
        # Download image content if it's not a self post
        if not post.is_self:
            try:
                response = requests.get(post.url)
                if response.status_code == 200:
                    image_data = response.content
                    post_data = post_data[:-1] + (image_data,)  # Replace the placeholder with image_data
                    print(f"Image downloaded successfully for post ID {post.id}")
                else:
                    print(f"Failed to download image for post ID {post.id}")
            except Exception as e:
                print(f"Error downloading image for post ID {post.id}: {e}")

        # Insert data into MySQL
        cursor.execute("""
            INSERT INTO posts (type, title, subreddit, url, score, upvote_ratio, comments, created_at, post_id, text_content, image_url, image_content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, post_data)

    comments = user.comments.new(limit=None)

    for comment in comments:
        comment_data = (
            "Comment",
            str(comment.subreddit),
            comment.score,
            datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            comment.id,
            comment.parent_id,
            comment.body
        )
        
        cursor.execute("""
            INSERT INTO comments (type, subreddit, score, created_at, comment_id, parent_id, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, comment_data)

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Received Reddit User ID and stored data successfully'})

#------------END--OF--REDDIT---------------

#----------------SPOTIFY-------------------

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

#----------------END--OF--SPOTIFY---------------------



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=4000)

