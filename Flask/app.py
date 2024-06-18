from flask import Flask, request, jsonify
from flask_cors import CORS

# reddit API package
import praw
from datetime import datetime
import requests
import os
import json
import zipfile
import shutil
from flask import send_file


app = Flask(__name__)
CORS(app)  

@app.route('/api/reddit', methods=['POST'])
def receive_reddit_id():
    data = request.get_json()
    reddit_id = data.get('reddit_id')
    print(f"Received Reddit User ID: {reddit_id}")

    return jsonify({'message': 'Received Reddit User ID successfully'})

if __name__ == '__main__':
    app.run(debug=True)
