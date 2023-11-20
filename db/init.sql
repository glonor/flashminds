-- Create a new database for flashcard records
CREATE DATABASE IF NOT EXISTS flashcard_db;
USE flashcard_db;

-- Create a table for users
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY, -- User identifier
    username VARCHAR(50) NOT NULL, -- User username
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for decks
CREATE TABLE IF NOT EXISTS decks (
    deck_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    deck_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create a table for flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    deck_id INT,
    question VARCHAR(255) NOT NULL,
    answer VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id) ON DELETE CASCADE
);

-- Create a table for study sessions
CREATE TABLE IF NOT EXISTS study_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    deck_id INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id) ON DELETE CASCADE  -- Add ON DELETE CASCADE
);

-- Create a table to store flashcard confidences in each study session
CREATE TABLE IF NOT EXISTS flashcard_confidences (
    confidence_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    card_id INT,
    confidence INT CHECK (confidence >= 1 AND confidence <= 5),
    FOREIGN KEY (session_id) REFERENCES study_sessions(session_id) ON DELETE CASCADE,  -- Add ON DELETE CASCADE
    FOREIGN KEY (card_id) REFERENCES flashcards(card_id) ON DELETE CASCADE  -- Add ON DELETE CASCADE
);


-- Sample data for users
INSERT INTO users (user_id, username) VALUES
    (123456, 'john_doe'), -- User 1 with User ID 123456 and username 'john_doe'
    (789012, 'jane_smith'); -- User 2 with User ID 789012 and username 'jane_smith'

-- Sample data for decks
INSERT INTO decks (user_id, deck_name) VALUES
    (123456, 'Mathematics'), -- User 1's Mathematics deck
    (123456, 'History'), -- User 1's History deck
    (789012, 'Biology'); -- User 2's Biology deck

-- Sample data for cards
INSERT INTO flashcards (deck_id, question, answer) VALUES
    (1, 'What is 2 + 2?', '4'),
    (1, 'Who was the first president of the USA?', 'George Washington'),
    (2, 'What is the powerhouse of the cell?', 'Mitochondria');

-- Sample data for study sessions
INSERT INTO study_sessions (user_id, deck_id, start_time, end_time) VALUES
    (123456, 1, '2023-01-01 10:00:00', '2023-01-01 11:30:00'), -- User 1 studies Mathematics
    (123456, 2, '2023-01-02 14:00:00', '2023-01-02 15:30:00'), -- User 1 studies History
    (789012, 3, '2023-01-03 09:00:00', '2023-01-03 10:30:00'); -- User 2 studies Biology

-- Sample data for flashcard confidences
INSERT INTO flashcard_confidences (session_id, card_id, confidence) VALUES
    (1, 1, 4), -- User 1's Mathematics session, Card 1 confidenced 4
    (1, 2, 5); -- User 1's Mathematics session, Card 2 confidenced 5

