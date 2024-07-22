from flask import Flask, session, request

app = Flask(__name__)

# Set a secure secret key for production (replace with a strong, random string)
app.config['SECRET_KEY'] = 'your_secret_key_here'

@app.route('/set_user_id/<user_id>')
def set_user_id(user_id):
    """Sets the user ID in the session and prints a confirmation message."""
    session['user_id'] = user_id
    print("session id: ",request.cookies,"dict session : ",dict(session))
    return f"User ID {user_id} set in session."

@app.route('/get_user_id')
def get_user_id():
    """Retrieves and prints the user ID from the session, handling potential errors."""
    print("sessiosion user_id:",session['user_id'])
    user_id = session.get('user_id')
    if user_id is None:
        return "No user ID found in session."
    return f"User ID retrieved from session: {user_id}"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=2000)

