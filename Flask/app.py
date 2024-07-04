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

        
    # Reddit credential secret
    CLIENT_ID = 'vDlSP0b2Loia3loPC1ObsQ'
    CLIENT_SECRET = '6fGr2o1BqgMdAdTWePHLSJwozfimyw'
    USER_AGENT = 'RedditPostFetcher/1.0 by Warm-Cucumber-3293'

    # target user name
    TARGET_USER = str(reddit_id)
    # ex. ARGET_USER = 'Warm-Cucumber-3293'

    # to store all the list and content of the user
    user_all_data = []


    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    
    user = reddit.redditor(TARGET_USER)
    posts = user.submissions.new(limit=None)

    
    user_folder = os.path.join('content', TARGET_USER)
    os.makedirs(user_folder, exist_ok=True)

   
    for post in posts:

        user_database = {
            "Type": "Post",
            "Title": post.title,
            "Subreddit": str(post.subreddit),
            "URL": post.url,
            "Score": post.score,
            "Upvote Ratio": post.upvote_ratio,
            "Comments": post.num_comments,
            "Unix timestamp Created at": post.created_utc,
            "Created at": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "Post ID": post.id,
            "Text-based Content": post.selftext if post.is_self else None,
            "Image Content URL": post.url if not post.is_self else None
        }

    
        
        if post.is_self:
            
            print(f"Text-based Content: {post.selftext}")
        else:
            
            print(f"Image Content URL: {post.url}")

            image_url = post.url
            file_extension = os.path.splitext(image_url)[1]

            if not file_extension:
                
                file_extension = '.jpg'
    

            
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                    # image_filename = os.path.join('content/', f'{post.id}.jpg')
                    # image_filename = os.path.join('content', f'{post.id}{file_extension}')
                    image_filename = os.path.join(user_folder, f'{post.id}{file_extension}')
                    with open(image_filename, 'wb') as image_file:
                        image_file.write(image_data)
                    print(f"Image downloaded successfully: {image_filename}, saved to {image_filename}")
                else:
                    print(f"Failed to download image: {image_url}")
            except Exception as e:
                print(f"Error downloading image: {e}")
            
        print("=" * 40)
        user_all_data.append(user_database)


    
    user = reddit.redditor(TARGET_USER)
    comments = user.comments.new(limit=None)

    
    for comment in comments:

        comment_database = {
            "Type": "Comment",
            "Subreddit": str(comment.subreddit),
            "Score": comment.score,
            "Unix timestamp Created at": comment.created_utc,
            "Created at": datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "Comment ID": comment.id,
            "Parent ID": comment.parent_id,
            "Content": comment.body
        }


        # print(f"Subreddit: {comment.subreddit}")
        # print(f"Score: {comment.score}")
        # print(f"Unix timestamp Created at: {comment.created_utc}")
        # created_at = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        # print(f"Created at: {created_at}")
        # print(f"Comment ID: {comment.id}")
        # print(f"Parent ID: {comment.parent_id}")
        # print(f"Content: {comment.body}")
        # print("*" * 40)

        user_all_data.append(comment_database)



    print(user_all_data)

    
    output_file = os.path.join(user_folder, 'user_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(user_all_data, f, ensure_ascii=False, indent=4)

    print(f"All posts data saved to {output_file}")

    shutil.make_archive(user_folder, 'zip', user_folder)
    zip_filename = f'{reddit_id}.zip'
    print("--")
    print(zip_filename)
    print(f'{user_folder}.zip')
    print("--")

    return send_file(f'{user_folder}.zip', as_attachment=True, download_name=zip_filename)
    # return jsonify({'message': 'Received Reddit User ID successfully'})

if __name__ == '__main__':
    app.run(debug=True)
