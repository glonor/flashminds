-- Create a new database for flashcards records
CREATE DATABASE IF NOT EXISTS flashcard_db;
USE flashcard_db;

-- Create a table to store users
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table to store flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    front_content VARCHAR(255) NOT NULL,
    back_content VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Sample data (you can customize or remove this part)

INSERT INTO users (user_id) VALUES (1), (2), (3);

INSERT INTO flashcards (front_content, back_content) VALUES
    (1, 'Capital of France', 'Paris'),
    (2, 'Largest mammal', 'Blue Whale'),
    (3, 'Programming language for web development', 'JavaScript');
