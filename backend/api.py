import pymysql
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# API Base URL
BANANA_API_URL = "https://marcconrad.com/uob/banana/api.php"

# Database connection function
def get_db_connection():
    return pymysql.connect(host="localhost", user="root", password="root", database="banana_game", cursorclass=pymysql.cursors.DictCursor)

def fetch_question(level):
    """Fetch a question from the API and store it in the database."""
    url = f"{BANANA_API_URL}?difficulty={level}"  # API endpoint

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            question_data = response.json()

            # Extract question details
            image_url = question_data.get("question", "")  # API returns image URL in "question"
            solution = question_data.get("solution", "")

            if not image_url or not solution:
                return {"error": "Invalid response from API. Missing 'question' or 'solution'."}

            # Store in the database and get the correct question_id
            question_id = store_question_in_db(image_url, solution)

            if question_id:
                return {
                    "image_url": image_url,
                    "solution": solution,
                    "question_id": question_id  # Return correct question_id
                }
            else:
                return {"error": "Failed to store question in the database."}

        else:
            return {"error": f"Failed to fetch question. Status Code: {response.status_code}"}

    except requests.Timeout:
        return {"error": "Request timed out. Please try again later."}

    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def store_question_in_db(image_url, solution):
    """Store the question in the database and return the question_id."""
    try:
        # Assuming you're using a database connection here
        db = get_db()  # Replace with your DB connection function
        cursor = db.cursor()

        # Insert the question into the game_questions table
        cursor.execute(
            "INSERT INTO game_questions (image_url, solution) VALUES (%s, %s)",
            (image_url, solution)
        )
        db.commit()  # Commit the changes to the database

        # Fetch the last inserted question_id
        cursor.execute("SELECT LAST_INSERT_ID()")
        question_id = cursor.fetchone()[0]

        return question_id  # Return the question_id

    except Exception as e:
        print(f"Error storing question in DB: {str(e)}")
        return None

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def store_question_in_db(image_url, solution, level="easy"):
    """Stores fetched question in MySQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the question already exists
        query_check = "SELECT * FROM game_questions WHERE image_url = %s"
        cursor.execute(query_check, (image_url,))
        existing_question = cursor.fetchone()

        if not existing_question:  # Insert only if not already in DB
            query_insert = "INSERT INTO game_questions (image_url, solution, level) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (image_url, solution, level))
            conn.commit()
        
        # Fetch the question_id after inserting
        cursor.execute("SELECT question_id FROM game_questions WHERE image_url = %s", (image_url,))
        stored_question = cursor.fetchone()
        
        if stored_question:
            return stored_question["question_id"]  # Return correct question_id
        
    except Exception as e:
        print("Database insert error:", e)
    
    finally:
        cursor.close()
        conn.close()

