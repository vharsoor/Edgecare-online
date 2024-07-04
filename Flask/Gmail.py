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

app = Flask(__name__)
CORS(app)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/calendar.readonly'
]

TOKEN_PATH = 'token.pickle'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def get_credentials(credentials_path):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

@app.route('/api/google_auth', methods=['POST'])
def api_get_credentials():
    if 'credentials_path' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['credentials_path']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file:
        credentials_path = os.path.join('.', file.filename)
        file.save(credentials_path)
        auth_url = get_credentials(credentials_path)
        return jsonify({'auth_url': auth_url}), 200
    
    return jsonify({'message': 'File upload failed'}), 500

@app.route('/api/exchange_code', methods=['POST'])
def exchange_code():
    code = request.json.get('code')
    credentials_path = request.json.get('credentials_path')
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    
    creds = flow.credentials
    app.config['creds'] = creds
    
    return jsonify({'message': 'Credentials obtained successfully'}), 200

@app.route('/api/gmail_collect')
def api_gmail_collect():
    emails = gmail_collect(app.config['creds'])
    return jsonify(emails), 200

@app.route('/api/fetch_calendar_events')
def api_fetch_calendar_events():
    events = fetch_calendar_events(app.config['creds'])
    return jsonify(events), 200

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

    return {'received_emails': received_emails, 'sent_emails': sent_emails}

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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=4000)
