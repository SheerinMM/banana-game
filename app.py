from flask import Flask, render_template, request, redirect, url_for, session
from backend.db import get_db

app = Flask(__name__)
app.secret_key = "your_secret_key"

db = get_db()

class MySQLAuth:
    @staticmethod
    def signup(username, email, password):
        try:
            # Store user data in MySQL
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, password))
            db.commit()
            cursor.close()
            return "User registered successfully"
        except Exception as e:
            print("Signup error:", e)
            return None

    @staticmethod
    def login(email, password):
        try:
            # Verify user exists in MySQL
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            cursor.close()

            if user_data and user_data['password'] == password:  # Verify password
                return user_data  # Return user details from MySQL
            else:
                return None
        except Exception as e:
            print("Login error:", e)
            return None

mysql_auth = MySQLAuth()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = mysql_auth.signup(username, email, password)
        if user:
            session['username'] = username
            session['email'] = email
            return redirect(url_for('game'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = mysql_auth.login(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('game'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/game')
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('game.html', username=session.get('username'))

@app.route('/level')
def level():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('level.html', username=session.get('username'))

@app.route('/score')
def score():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT score, date 
            FROM scores 
            WHERE user_id = %s 
            ORDER BY date DESC
        """, (session['user_id'],))
        user_scores = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching user scores:", e)
        user_scores = []

    return render_template('score.html', user_scores=user_scores)


@app.route('/leaderboard/<int:page>')
def leaderboard(page=1):
    try:
        limit = 10  # Show 10 records per page
        offset = (page - 1) * limit
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT users.username, scores.score 
            FROM scores 
            JOIN users ON scores.user_id = users.user_id 
            ORDER BY scores.score DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        scores = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching leaderboard data:", e)
        scores = []

    return render_template('leaderboard.html', scores=scores, page=page)



if __name__ == '__main__':
    app.run(debug=True)
