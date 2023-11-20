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
    telegram_id = data.get('telegram_id')

    if telegram_id is None:
        return jsonify({'error': 'telegram_id parameter is missing'}), 400

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if the telegram_id is present in the database
        cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
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
    telegram_id = data.get('telegram_id')

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Insert user data into the database
        query = "INSERT INTO users (telegram_id) VALUES (%s)"
        values = (telegram_id,)
        cursor.execute(query, values)
        connection.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error creating user: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


@app.route('/add_flashcard', methods=['POST'])
def add_flashcard():
    """
    This route handles the submission of flashcard data via a POST request.
    It retrieves the form data, validates it, and inserts the flashcard data into the database.
    """
    # Get form data
    question = request.form['question']
    answer = request.form['answer']

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Insert flashcard data into the database
        query = "INSERT INTO flashcards (question, answer) VALUES (%s, %s)"
        values = (question, answer)
        cursor.execute(query, values)
        connection.commit()
        return jsonify({'message': 'Flashcard added successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error adding flashcard: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


@app.route('/flashcard_data', methods=['GET'])
def get_flashcard_data():
    """
    This route retrieves flashcard data from the database and returns it as JSON.
    It responds to GET requests and provides a list of flashcard front and back contents.
    """
    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # SQL query to retrieve flashcard data
        cursor.execute('SELECT question, answer FROM flashcards')
        results = cursor.fetchall()
        return jsonify({'flashcard_data': results})
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error fetching flashcard data: {err}'}), 500
    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
