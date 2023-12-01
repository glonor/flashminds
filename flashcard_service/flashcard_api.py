import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

# Database configuration for student records
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'flashcard_db',
    'auth_plugin': 'mysql_native_password'
}

# Function to create a database connection
def create_db_connection():
    return mysql.connector.connect(**db_config)    
    
# Check if the user exists
def check_user_exists(cursor, user_id):
    check_query = "SELECT 1 FROM users WHERE user_id = %s"
    check_values = (user_id,)
    cursor.execute(check_query, check_values)
    user_exists = cursor.fetchone()

    return user_exists is not None
    
# Check if a deck with the same name already exists for the specified user
def check_deck_name_exists(cursor, user_id, deck_name):
    check_query = "SELECT 1 FROM decks WHERE user_id = %s AND deck_name = %s"
    check_values = (user_id, deck_name)
    cursor.execute(check_query, check_values)
    deck_exists = cursor.fetchone()

    return deck_exists is not None

# Check if the deck exists and belongs to the user
def check_deck_exists(cursor, user_id, deck_id):
    check_query = "SELECT 1 FROM decks WHERE user_id = %s AND deck_id = %s"
    check_values = (user_id, deck_id)
    cursor.execute(check_query, check_values)
    deck_exists = cursor.fetchone()

    return deck_exists is not None

# Endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        if 'user_id' not in data or 'username' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        user_id = data.get('user_id')
        username = data.get('username')

        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if user_exists:
            return jsonify({'message': 'User with the same user_id already exists'}), 409

        # Insert user data into the database
        query = "INSERT INTO users (user_id, username) VALUES (%s, %s)"
        values = (user_id, username)
        cursor.execute(query, values)
        connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to get a specific user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve user data from the database
        query = "SELECT * FROM users WHERE user_id = %s"
        values = (user_id,)
        cursor.execute(query, values)
        user = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if user is None:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    

# Endpoint to update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()

        if 'username' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        username = data.get('username')

        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Update user data in the database
        query = "UPDATE users SET username = %s WHERE user_id = %s"
        values = (username, user_id)
        cursor.execute(query, values)
        connection.commit()

        # Check if any rows were affected
        rows_affected = cursor.rowcount

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error updating user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    

# Endpoint to delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:        
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404

        # Delete user data from the database
        query = "DELETE FROM users WHERE user_id = %s"
        values = (user_id,)
        cursor.execute(query, values)
        connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error deleting user: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    

# Endpoint to create a new deck
@app.route('/users/<int:user_id>/decks', methods=['POST'])
def create_deck(user_id):
    try:
        data = request.get_json()

        if 'deck_name' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        deck_name = data.get('deck_name')
        
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if a deck with the same name already exists for the specified user
        deck_exists = check_deck_name_exists(cursor, user_id, deck_name)

        if deck_exists:
            return jsonify({'message': 'Deck with the same name already exists'}), 409  # Conflict

        # Insert deck data into the database
        query = "INSERT INTO decks (user_id, deck_name) VALUES (%s, %s)"
        values = (user_id, deck_name)
        cursor.execute(query, values)

        # Fetch the deck_id from the last inserted row
        cursor.execute("SELECT LAST_INSERT_ID()")
        deck_id = cursor.fetchone()[0]
        
        connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'Deck created successfully', 'deck_id': deck_id}), 201
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error creating deck: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500


# Endpoint to update a deck
@app.route('/users/<int:user_id>/decks/<int:deck_id>', methods=['PUT'])
def update_deck(user_id, deck_id):
    try:
        data = request.get_json()

        if 'deck_name' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        deck_name = data.get('deck_name')

        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if a deck with the same name already exists for the specified user
        deck_exists = check_deck_name_exists(cursor, user_id, deck_name)

        if deck_exists:
            return jsonify({'message': 'Deck with the same name already exists'}), 409  # Conflict
        
        # Update deck data in the database
        query = "UPDATE decks SET deck_name = %s WHERE deck_id = %s AND user_id = %s"
        values = (deck_name, deck_id, user_id)
        cursor.execute(query, values)
        connection.commit()

        # Check if any rows were affected
        rows_affected = cursor.rowcount

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'message': 'Deck not found'}), 404
        return jsonify({'message': 'Deck updated successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error updating deck: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500


# Endpoint to get decks for a specific user
@app.route('/users/<int:user_id>/decks', methods=['GET'])
def get_decks(user_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

         # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404

        # Retrieve decks and the count of flashcards for the specified user
        query = """
            SELECT decks.*, COUNT(flashcards.card_id) AS flashcard_count
            FROM decks
            LEFT JOIN flashcards ON decks.deck_id = flashcards.deck_id
            WHERE decks.user_id = %s
            GROUP BY decks.deck_id
            ORDER BY decks.created_at DESC
        """
        values = (user_id,)
        cursor.execute(query, values)
        decks = cursor.fetchall()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()
        
        return jsonify({'decks': decks}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting decks: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to get a specific deck
@app.route('/users/<int:user_id>/decks/<int:deck_id>', methods=['GET'])
def get_deck(user_id, deck_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        
         # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404

        # Retrieve deck and the count of flashcards for the specified user
        query = """
            SELECT decks.*, COUNT(flashcards.card_id) AS flashcard_count
            FROM decks
            LEFT JOIN flashcards ON decks.deck_id = flashcards.deck_id
            WHERE decks.deck_id = %s AND decks.user_id = %s
            GROUP BY decks.deck_id
        """
        values = (deck_id, user_id)
        cursor.execute(query, values)
        deck = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if deck is None:
            return jsonify({'message': 'Deck not found'}), 404
        
        return jsonify({'deck': deck}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting deck: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

    
# Endpoint to delete a deck
@app.route('/users/<int:user_id>/decks/<int:deck_id>', methods=['DELETE'])
def delete_deck(user_id, deck_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

         # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404

        # Delete deck data from the database
        query = "DELETE FROM decks WHERE deck_id = %s AND user_id = %s"
        values = (deck_id, user_id)
        cursor.execute(query, values)
        connection.commit()

        # Check if any rows were affected
        rows_affected = cursor.rowcount

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'message': 'Deck not found'}), 404
        return jsonify({'message': 'Deck deleted successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error deleting deck: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    

# Endpoint to create a new flashcard
@app.route('/users/<int:user_id>/decks/<int:deck_id>/flashcards', methods=['POST'])
def create_flashcard(user_id, deck_id):
    try:
        data = request.get_json()

        if 'question' not in data or 'answer' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        question = data.get('question')
        answer = data.get('answer')

        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Insert flashcard data into the database
        query = "INSERT INTO flashcards (deck_id, question, answer) VALUES (%s, %s, %s)"
        values = (deck_id, question, answer)
        cursor.execute(query, values)

        # Fetch the deck_id from the last inserted row
        cursor.execute("SELECT LAST_INSERT_ID()")
        card_id = cursor.fetchone()[0]

        connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'Flashcard created successfully', 'card_id': card_id}), 201
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error creating flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# Endpoint to update a flashcard
@app.route('/users/<int:user_id>/decks/<int:deck_id>/flashcards/<int:card_id>', methods=['PUT'])
def update_flashcard(user_id, deck_id, card_id):
    try:
        data = request.get_json()

        if 'ebisu_model' not in data or 'last_reviewed' not in data:
            return jsonify({'message': 'Missing required fields'}), 400
        
        ebisu_model = data.get('ebisu_model')
        last_reviewed = data.get('last_reviewed')
        
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Update flashcard data in the database
        query = "UPDATE flashcards SET ebisu_model = %s, last_reviewed = %s WHERE card_id = %s AND deck_id = %s"
        values = (ebisu_model, last_reviewed, card_id, deck_id)
        cursor.execute(query, values)
        connection.commit()
        
        # Check if any rows were affected
        rows_affected = cursor.rowcount
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'message': 'Flashcard not found'}), 404
        return jsonify({'message': 'Flashcard updated successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error updating flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# Endpoint to get flashcards for a specific deck
@app.route('/users/<int:user_id>/decks/<int:deck_id>/flashcards', methods=['GET'])
def get_flashcards(user_id, deck_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Retrieve flashcards for the specified deck
        query = "SELECT * FROM flashcards WHERE deck_id = %s"
        values = (deck_id,)
        cursor.execute(query, values)
        flashcards = cursor.fetchall()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if not flashcards:
            return jsonify({'message': 'No flashcards found for the specified deck'}), 404
        
        return jsonify({'flashcards': flashcards}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting flashcards: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to get a specific flashcard
@app.route('/users/<int:user_id>/decks/<int:deck_id>/flashcards/<int:card_id>', methods=['GET'])
def get_flashcard(user_id, deck_id, card_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Retrieve flashcard for the specified deck
        query = "SELECT * FROM flashcards WHERE card_id = %s AND deck_id = %s"
        values = (card_id, deck_id)
        cursor.execute(query, values)
        flashcard = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if flashcard is None:
            return jsonify({'message': 'Flashcard not found'}), 404
        
        return jsonify({'flashcard': flashcard}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

    
# Endpoint to delete a flashcard
@app.route('/users/<int:user_id>/decks/<int:deck_id>/flashcards/<int:card_id>', methods=['DELETE'])
def delete_flashcard(user_id, deck_id, card_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Delete flashcard data from the database
        query = "DELETE FROM flashcards WHERE card_id = %s AND deck_id = %s"
        values = (card_id, deck_id)
        cursor.execute(query, values)
        connection.commit()

        # Check if any rows were affected
        rows_affected = cursor.rowcount

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'message': 'Flashcard not found'}), 404
        return jsonify({'message': 'Flashcard deleted successfully'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error deleting flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to create a new study session
@app.route('/users/<int:user_id>/decks/<int:deck_id>/study_sessions', methods=['POST'])
def create_study_session(user_id, deck_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Insert study session data into the database
        query = "INSERT INTO study_sessions (user_id, deck_id) VALUES (%s, %s)"
        values = (user_id, deck_id)
        cursor.execute(query, values)
        connection.commit()

        # Get the last inserted session_id
        session_id = cursor.lastrowid

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'Study session created successfully', 'session_id': session_id}), 201
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error creating study session: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

    
# Endpoint to get study sessions for a specific deck
@app.route('/users/<int:user_id>/decks/<int:deck_id>/study_sessions', methods=['GET'])
def get_study_sessions(user_id, deck_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Retrieve study sessions for the specified deck
        query = "SELECT * FROM study_sessions WHERE deck_id = %s AND user_id = %s"
        values = (deck_id, user_id)
        cursor.execute(query, values)
        study_sessions = cursor.fetchall()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if not study_sessions:
            return jsonify({'message': 'No study sessions found for the specified deck'}), 404
        
        return jsonify({'study_sessions': study_sessions}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting study sessions: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500
    
# Endpoint to get a specific study session
@app.route('/users/<int:user_id>/decks/<int:deck_id>/study_sessions/<int:session_id>', methods=['GET'])
def get_study_session(user_id, deck_id, session_id):
    try:
        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404

        # Retrieve study session for the specified deck
        query = "SELECT * FROM study_sessions WHERE deck_id = %s AND session_id = %s AND user_id = %s"
        values = (deck_id, session_id, user_id)
        cursor.execute(query, values)
        study_session = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if study_session is None:
            return jsonify({'message': 'Study session not found'}), 404
        
        return jsonify({'study_session': study_session}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error getting study session: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500


# Endpoint to update a study session
@app.route('/users/<int:user_id>/decks/<int:deck_id>/study_sessions/<int:session_id>', methods=['PUT'])
def update_study_session(user_id, deck_id, session_id):
    try:
        data = request.get_json()

        # Check if at least one field is present
        if 'confidence' not in data and 'end_time' not in data:
            return jsonify({'message': 'At least one field (confidence or end_time) is required'}), 400

        # Extract fields from the payload
        confidence = data.get('confidence')
        end_time = data.get('end_time')

        # Create a database connection and cursor
        connection = create_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        user_exists = check_user_exists(cursor, user_id)

        if not user_exists:
            return jsonify({'message': 'User not found'}), 404

        # Check if the deck exists and belongs to the user
        deck_exists = check_deck_exists(cursor, user_id, deck_id)

        if not deck_exists:
            return jsonify({'message': 'Deck not found'}), 404
        
        # Check if the study session exists
        query = "SELECT 1 FROM study_sessions WHERE session_id = %s AND deck_id = %s"
        values = (session_id, deck_id)
        cursor.execute(query, values)
        session_exists = cursor.fetchone()

        if session_exists is None:
            return jsonify({'message': 'Study session not found'}), 404

        # Build the query dynamically based on the fields present
        query = "UPDATE study_sessions SET"
        values = []

        if 'confidence' in data:
            query += " average_confidence = %s,"
            values.append(confidence)

        if 'end_time' in data:
            query += " end_time = %s,"
            values.append(end_time)

        # Remove the trailing comma from the query
        query = query.rstrip(',')

        # Add the common conditions to the query
        query += " WHERE session_id = %s AND deck_id = %s"
        values.extend([session_id, deck_id])

        # Execute the query
        cursor.execute(query, values)
        connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'Study session updated successfully'}), 200

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error updating study session: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')
