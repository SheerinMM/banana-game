-- Use the database
USE banana_game;

-- Insert sample users (passwords should be hashed in real cases)
INSERT INTO users (username, email, password) 
VALUES 
('player1', 'player1@example.com', 'hashed_password_1'),
('player2', 'player2@example.com', 'hashed_password_2'),
('player3', 'player3@example.com', 'hashed_password_3');

-- Insert sample scores
INSERT INTO scores (user_id, score) 
VALUES 
(1, 50),
(2, 75),
(3, 30),
(1, 90),
(2, 60);
