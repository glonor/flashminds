-- Create a new database for flashcards records
CREATE DATABASE IF NOT EXISTS flashcard_db;
USE flashcard_db;

-- Create a table to store users
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table to store decks
CREATE TABLE IF NOT EXISTS decks (
    deck_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    deck_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create a table to store flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    deck_id INT,
    front_content VARCHAR(255) NOT NULL,
    back_content VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

-- Sample data (you can customize or remove this part)
INSERT INTO users (user_id) VALUES
    (1),
    (2),
    (3);

INSERT INTO decks (user_id, deck_name) VALUES
    (1, 'French Vocabulary'),
    (2, 'Biology Facts'),
    (3, 'Web Development');

INSERT INTO flashcards (deck_id, front_content, back_content) VALUES
    (1, 'Capital of France', 'Paris'),
    (1, 'Common Phrases', 'Bonjour'),
    (2, 'Largest mammal', 'Blue Whale'),
    (2, 'Human Anatomy', 'Femur'),
    (3, 'Programming language for web development', 'JavaScript'),
    (3, 'Front-end framework', 'React');
