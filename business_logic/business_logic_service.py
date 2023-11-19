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


@app.route('/')
def index():
    """
    This route provides a welcome message when accessing the root URL.
    """
    return jsonify({'message': 'Welcome to the FlashMinds API'})


@app.route('/add_flashcard', methods=['POST'])
def add_flashcard():
    """
    This route handles the submission of flashcard data via a POST request.
    It retrieves the form data, validates it, and inserts the flashcard data into the database.
    """
    # Get form data
    front_content = request.form['front_content']
    back_content = request.form['back_content']

    # Create a database connection and cursor
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Insert flashcard data into the database
        query = "INSERT INTO flashcards (front_content, back_content) VALUES (%s, %s)"
        values = (front_content, back_content)
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
        cursor.execute('SELECT front_content, back_content FROM flashcards')
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
