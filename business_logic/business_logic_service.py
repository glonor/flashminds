from flask import Flask, jsonify, request, render_template
import mysql.connector

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

# Endpoint to check if user is present in the database
@app.route('/check_user', methods=['GET'])
def check_user():
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({'error': 'user_id parameter is missing'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if the user_id is present in the database
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        result = cursor.fetchone()

        if result:
            return jsonify({'message': 'User found'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error checking user: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

# Endpoint to create a new user
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get('user_id')
    user_name = data.get('user_name')

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Insert user data into the database
        query = "INSERT INTO users (user_id, user_name) VALUES (%s, %s)"
        values = (user_id, user_name)
        cursor.execute(query, values)
        connection.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error creating user: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

# Endpoint to create a new deck for a user
@app.route('/create_deck', methods=['POST'])
def create_deck():
    data = request.get_json()
    user_id = data.get('user_id')
    deck_name = data.get('deck_name')

    if user_id is None or deck_name is None:
        return jsonify({'error': 'user_id and deck_name parameters are required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the user with the given user_id exists
        user_check_query = "SELECT * FROM users WHERE user_id = %s"
        user_check_values = (user_id,)
        cursor.execute(user_check_query, user_check_values)
        existing_user = cursor.fetchone()

        if not existing_user:
            return jsonify({'error': 'User with the provided user_id does not exist'}), 404

        # Check if the deck name is already taken for the given user_id
        deck_check_query = "SELECT * FROM decks WHERE user_id = %s AND deck_name = %s"
        deck_check_values = (user_id, deck_name)
        cursor.execute(deck_check_query, deck_check_values)
        existing_deck = cursor.fetchone()

        if existing_deck:
            return jsonify({'error': 'Deck name already exists'}), 409

        # Insert deck data into the database
        insert_query = "INSERT INTO decks (user_id, deck_name) VALUES (%s, %s)"
        insert_values = (user_id, deck_name)
        cursor.execute(insert_query, insert_values)
        connection.commit()

        return jsonify({'message': 'Deck created successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error creating deck: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

# Endpoint to get decks for a specific user
@app.route('/get_decks', methods=['GET'])
def get_decks():
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({'error': 'user_id parameter is required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if the user exists
        user_check_query = "SELECT * FROM users WHERE user_id = %s"
        user_check_values = (user_id,)
        cursor.execute(user_check_query, user_check_values)
        existing_user = cursor.fetchone()

        if not existing_user:
            return jsonify({'error': 'User with the provided user_id does not exist'}), 404

        # Retrieve decks for the specified user
        decks_query = "SELECT * FROM decks WHERE user_id = (SELECT user_id FROM users WHERE user_id = %s)"
        decks_values = (user_id,)
        cursor.execute(decks_query, decks_values)
        decks = cursor.fetchall()

        return jsonify({'decks': decks}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error retrieving decks: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


# Endpoint to add a new flashcard
@app.route('/add_flashcard', methods=['POST'])
def add_flashcard():
    data = request.get_json()
    user_id = data.get('user_id')
    deck_id = data.get('deck_id')
    question = data.get('question')
    answer = data.get('answer')

    if user_id is None or deck_id is None or question is None or answer is None:
        return jsonify({'error': 'user_id, deck_id, question, and answer parameters are required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the user with the given user_id exists
        user_check_query = "SELECT * FROM users WHERE user_id = %s"
        user_check_values = (user_id,)
        cursor.execute(user_check_query, user_check_values)
        existing_user = cursor.fetchone()

        if not existing_user:
            return jsonify({'error': 'User with the provided user_id does not exist'}), 404

        # Check if the deck with the given deck_id and associated with the provided user_id exists
        deck_check_query = "SELECT * FROM decks WHERE deck_id = %s AND user_id = (SELECT user_id FROM users WHERE user_id = %s)"
        deck_check_values = (deck_id, user_id)
        cursor.execute(deck_check_query, deck_check_values)
        existing_deck = cursor.fetchone()

        if not existing_deck:
            return jsonify({'error': 'Deck with the provided deck_id and associated with the provided user_id does not exist'}), 404

        # Insert flashcard data into the database
        flashcard_query = "INSERT INTO flashcards (deck_id, question, answer) VALUES (%s, %s, %s)"
        flashcard_values = (deck_id, question, answer)
        cursor.execute(flashcard_query, flashcard_values)
        connection.commit()

        return jsonify({'message': 'Flashcard added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error adding flashcard: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


# Endpoint to get flashcards for a specific deck
@app.route('/get_flashcards', methods=['GET'])
def get_flashcards():
    data = request.get_json()
    deck_id = data.get('deck_id')

    if deck_id is None:
        return jsonify({'error': 'deck_id parameter is required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if the deck exists
        deck_check_query = "SELECT * FROM decks WHERE deck_id = %s"
        deck_check_values = (deck_id,)
        cursor.execute(deck_check_query, deck_check_values)
        existing_deck = cursor.fetchone()

        if not existing_deck:
            return jsonify({'error': 'Deck with the provided deck_id does not exist'}), 404

        # Retrieve flashcards for the specified deck
        flashcards_query = "SELECT * FROM flashcards WHERE deck_id = %s"
        flashcards_values = (deck_id,)
        cursor.execute(flashcards_query, flashcards_values)
        flashcards = cursor.fetchall()

        return jsonify({'flashcards': flashcards}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error retrieving flashcards: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


# Endpoint to remove a flashcard
@app.route('/remove_flashcard', methods=['DELETE'])
def remove_flashcard():
    data = request.get_json()
    card_id = data.get('card_id')

    if card_id is None:
        return jsonify({'error': 'card_id parameter is required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the flashcard with the given card_id exists
        flashcard_check_query = "SELECT * FROM flashcards WHERE card_id = %s"
        flashcard_check_values = (card_id,)
        cursor.execute(flashcard_check_query, flashcard_check_values)
        existing_flashcard = cursor.fetchone()

        if not existing_flashcard:
            return jsonify({'error': 'Flashcard with the provided card_id does not exist'}), 404

        # Remove the flashcard from the database
        remove_query = "DELETE FROM flashcards WHERE card_id = %s"
        remove_values = (card_id,)
        cursor.execute(remove_query, remove_values)
        connection.commit()

        return jsonify({'message': 'Flashcard and associated data removed successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error removing flashcard: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()



# Endpoint to remove a deck
@app.route('/remove_deck', methods=['DELETE'])
def remove_deck():
    data = request.get_json()
    deck_id = data.get('deck_id')

    if deck_id is None:
        return jsonify({'error': 'deck_id parameter is required'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the deck with the given deck_id exists
        deck_check_query = "SELECT * FROM decks WHERE deck_id = %s"
        deck_check_values = (deck_id,)
        cursor.execute(deck_check_query, deck_check_values)
        existing_deck = cursor.fetchone()

        if not existing_deck:
            return jsonify({'error': 'Deck with the provided deck_id does not exist'}), 404

        # Remove the deck from the database
        remove_query = "DELETE FROM decks WHERE deck_id = %s"
        remove_values = (deck_id,)
        cursor.execute(remove_query, remove_values)
        connection.commit()

        return jsonify({'message': 'Deck and associated data removed successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error removing deck: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()



if __name__ == '__main__':
    app.run(host='0.0.0.0')
