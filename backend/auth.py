import os
from backend.db import get_db

class MySQLAuth:
    @staticmethod
    def signup(username, email, password):
        try:
            # Store user data in MySQL
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, password))
            db.commit()

            cursor.close()
            db.close()
            return "User registered successfully"
        except Exception as e:
            print("Signup error:", e)
            return None

    @staticmethod
    def login(email, password):
        try:
            # Verify user exists in MySQL
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            cursor.close()
            db.close()

            if user_data and user_data['password'] == password:  # Verify password
                return user_data  # Return user details from MySQL
            else:
                return None
        except Exception as e:
            print("Login error:", e)
            return None

mysql_auth = MySQLAuth()
