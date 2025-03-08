from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from backend.api import fetch_question
import json
from backend.db import get_db



# Establish database connection
db = get_db()

if db is None:
    raise Exception("❌ Database connection failed. Check your credentials and database status.")

cursor = db.cursor(dictionary=True)  # Now db is properly defined


app = Flask(__name__)
app.secret_key = "your_secret_key"



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

@app.route('/scoreboard')
def scoreboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.username, s.score, s.difficulty, s.time_taken, s.date 
            FROM scores s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.difficulty, s.score DESC, s.time_taken ASC, s.date DESC
        """)
        all_scores = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print("Error fetching scoreboard:", e)
        all_scores = []

    return render_template('score.html', all_scores=all_scores)




@app.route('/leaderboard')
def leaderboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT users.username, scores.score 
        FROM scores 
        JOIN users ON scores.user_id = users.user_id 
        ORDER BY score DESC 
        LIMIT 10
    """)
    scores = cursor.fetchall()
    cursor.close()
    return render_template('leaderboard.html', scores=scores)


    return render_template('leaderboard.html', scores=scores, page=page)

@app.route("/play")
def play():
    level = request.args.get("level", "easy")  # Get selected level
    question_data = fetch_question(level)  # Fetch from API & store in DB
    return render_template("play.html", level=level, question_data=question_data)

@app.route("/api/questions", methods=["GET"])

def get_question():
    """Fetch question from MySQL and return JSON response"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Fetch one random question
        cursor.execute("SELECT * FROM game_questions ORDER BY RAND() LIMIT 1")
        question = cursor.fetchone()

        if not question:
            return jsonify({"error": "No questions available"}), 404

        return jsonify(question)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()



# Fetch a random question from database


# Validate the answer
@app.route("/check_answer", methods=["POST"])
def check_answer():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Get user input
        user_answer = request.form.get("answer")
        question_id = request.form.get("question_id")

        if not user_answer or not question_id:
            return jsonify({"error": "Answer and question_id are required"}), 400

        try:
            question_id = int(question_id)  # Convert question_id to integer
        except ValueError:
            return jsonify({"error": "Invalid question ID format"}), 400

        # Fetch correct answer
        cursor.execute("SELECT solution FROM game_questions WHERE question_id = %s", (question_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return jsonify({"error": "Question not found"}), 404
        
        correct_answer = result["solution"]
        print(f"Checking Answer: {user_answer} vs {correct_answer}")  # Debugging
        
        # Compare answers after converting to lowercase and stripping spaces
        if user_answer.strip().lower() == correct_answer.strip().lower():
            return jsonify({"message": "Correct!"}), 200
        else:
            return jsonify({"message": f"Incorrect. "}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


@app.route("/submit_score", methods=["POST"])
def submit_score():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        user_id = session.get("user_id")
        level = request.form.get("level")  # Get level from frontend
        score = request.form.get("score")
        time_taken = request.form.get("time_taken")

        print(f"Received Data: user_id={user_id}, level={level}, score={score}, time_taken={time_taken}")  # Debug

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        if not level or not score or not time_taken:
            return jsonify({"error": "Missing data"}), 400

        # Convert to correct data types
        try:
            score = int(score)
            time_taken = float(time_taken)
        except ValueError:
            return jsonify({"error": "Invalid score or time format"}), 400

        # Insert into scores table
        cursor.execute("""
            INSERT INTO scores (user_id, level, score, time_taken, date)
            VALUES (%s, %s, %s, %s, NOW())
        """, (user_id, level, score, time_taken))
        
        db.commit()
        cursor.close()

        print("✅ Score successfully added to database!")  # Debug

        return jsonify({"message": "Score submitted successfully"}), 200

    except Exception as e:
        print(f"❌ Error submitting score: {str(e)}")  # Debug
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()







if __name__ == '__main__':
    app.run(debug=True)
