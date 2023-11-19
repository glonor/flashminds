-- Create a new database for flashcards records
CREATE DATABASE IF NOT EXISTS flashcard_db;
USE flashcard_db;

-- Create a table to store flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    front_content VARCHAR(255) NOT NULL,
    back_content VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data (you can customize or remove this part)
INSERT INTO flashcards (front_content, back_content) VALUES
    ('Capital of France', 'Paris'),
    ('Largest mammal', 'Blue Whale'),
    ('Programming language for web development', 'JavaScript');
