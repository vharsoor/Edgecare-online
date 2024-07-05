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

app = Flask(__name__)
CORS(app)

SCOPES = [
    #'openid',
    'https://www.googleapis.com/auth/calendar.readonly'
]

TOKEN_PATH = 'token.pickle'
#REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
REDIRECT_URI = 'https://edgecare.stresswatch.net/api/exchange_code'

def get_credentials(credentials_path):  
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

@app.route('/api/google_auth', methods=['POST'])
def api_get_credentials():
    #if 'credentials_path' not in request.files:
        #return jsonify({'message': 'No file part'}), 400
    
    #file = request.files['credentials_path']

    #if file.filename == '':
        #return jsonify({'message': 'No selected file'}), 400
    
    #if file:
    #credentials_path = os.path.join('.', file.filename)
    #file.save(credentials_path)
    credentials_path = os.path.expanduser('./google_creds.json')
    auth_url = get_credentials(credentials_path)
    return jsonify({'auth_url': auth_url}), 200
    
    return jsonify({'message': 'File upload failed'}), 500

@app.route('/api/exchange_code', methods=['GET'])
def exchange_code():
    #code = request.json.get('code')
    code= request.args.get('code')
    #credentials_path = request.json.get('credentials_path')
    credentials_path = os.path.expanduser('./google_creds.json')
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    
    creds = flow.credentials
    app.config['creds'] = creds
    
    return api_fetch_calendar_events()
    #return jsonify({'message': 'Credentials obtained successfully'}), 200


#@app.route('/api/fetch_calendar_events')
def api_fetch_calendar_events():
    events = fetch_calendar_events(app.config['creds'])
    return jsonify(events), 200


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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=4000)

