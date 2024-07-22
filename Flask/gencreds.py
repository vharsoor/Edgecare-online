import random
import string
import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

# RDS connection details
DATABASE_URL = "edge-care.c1c040sm422f.us-east-1.rds.amazonaws.com"
DATABASE_NAME = "edgecare"
DATABASE_USER = "admin"
DATABASE_PASSWORD = "root12345"
DATABASE_PORT = 3306

def get_db_connection():
    return pymysql.connect(
        host=DATABASE_URL,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )

def get_last_username():
    #conn = get_db_connection()
    conn = pymysql.connect(
        host=DATABASE_URL,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM user_credentials ORDER BY id DESC LIMIT 1")
        #esult = cursor.fetchone()
    except pymysql.MySQLError as e: #Case when table is not created yet
        print(f"Error: {e}")
        return None
    result = cursor.fetchone()
    conn.close()
    print("result : ",result)
    if result:
        return result[0]
    return None

#Like edgecare-001, edgecare-002, edgecare-003, etc.
def generate_next_username(last_username):
    print("lst:",last_username)
    if not last_username:
        return "edgecare-001"
    base, num = last_username.rsplit("-", 1)
    next_num = int(num) + 1
    return f"{base}-{next_num:03}"

def generate_random_password(length=4):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_credentials():
    last_username = get_last_username()
    new_username = generate_next_username(last_username)
    new_password = generate_random_password()
    return new_username, new_password

def store_credentials(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(20) UNIQUE,
            password VARCHAR(6)
        )
    ''')

    cursor.execute('''
        INSERT INTO user_credentials (username, password)
        VALUES (%s, %s)
    ''', (username, password))

    conn.commit()
    conn.close()

def check_credentials(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM user_credentials WHERE username = %s AND password = %s
    ''', (username, password))

    user = cursor.fetchone()
    conn.close()

    return user is not None

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if check_credentials(username, password):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid credentials."}), 401

if __name__ == "__main__":
    username, password = generate_random_credentials()
    store_credentials(username, password)
    print(f"Generated credentials - Username: {username}, Password: {password}")
    #app.run(debug=True, host='0.0.0.0', port=4000)

