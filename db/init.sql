-- Create a new database for flashcard records
CREATE DATABASE IF NOT EXISTS flashcard_db;
USE flashcard_db;

-- Create a table for users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id INT UNIQUE NOT NULL, -- Telegram identifier
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
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

-- Create a table for study sessions
CREATE TABLE IF NOT EXISTS study_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    deck_id INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

-- Create a table to store flashcard scores in each study session
CREATE TABLE IF NOT EXISTS flashcard_scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    card_id INT,
    score INT CHECK (score >= 1 AND score <= 5),
    FOREIGN KEY (session_id) REFERENCES study_sessions(session_id),
    FOREIGN KEY (card_id) REFERENCES flashcards(card_id)
);

-- Sample data for users
INSERT INTO users (user_id, telegram_id) VALUES
    (1, 123456), -- User 1 with Telegram ID 123456
    (2, 789012), -- User 2 with Telegram ID 789012
    (3, 345678); -- User 3 with Telegram ID 345678

-- Sample data for decks
INSERT INTO decks (user_id, deck_name) VALUES
    (1, 'Mathematics'), -- User 1's Mathematics deck
    (1, 'History'), -- User 1's History deck
    (2, 'Biology'); -- User 2's Biology deck

-- Sample data for cards
INSERT INTO flashcards (deck_id, question, answer) VALUES
    (1, 'What is 2 + 2?', '4'),
    (1, 'Who was the first president of the USA?', 'George Washington'),
    (2, 'What is the powerhouse of the cell?', 'Mitochondria');

-- Sample data for study sessions
INSERT INTO study_sessions (user_id, deck_id, start_time, end_time) VALUES
    (1, 1, '2023-01-01 10:00:00', '2023-01-01 11:30:00'), -- User 1 studies Mathematics
    (1, 2, '2023-01-02 14:00:00', '2023-01-02 15:30:00'), -- User 1 studies History
    (2, 3, '2023-01-03 09:00:00', '2023-01-03 10:30:00'); -- User 2 studies Biology

-- Sample data for flashcard scores
INSERT INTO flashcard_scores (session_id, card_id, score) VALUES
    (1, 1, 4), -- User 1's Mathematics session, Card 1 scored 4
    (1, 2, 5); -- User 1's Mathematics session, Card 2 scored 5

