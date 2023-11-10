CREATE DATABASE IF NOT EXISTS comp440_project;
USE comp440_project;

CREATE TABLE IF NOT EXISTS users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS item_categories (
    item_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (item_id, category_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS reviews (
	review_id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL,
    item_id INT NOT NULL,
    rating ENUM("excellent", "good", "fair", "poor") NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- Make admin
INSERT IGNORE INTO users (user_id, username, password, first_name, last_name, email)
VALUES (1, 'admin', 'admin', 'Max', 'Caulfield', 'admin@gmail.com');

-- Pre-defined categories
INSERT IGNORE INTO categories (category_name) 
VALUES 
    ('Electronics'),
    ('Fashion'),
    ('Home & Garden'),
    ('Toys & Games'),
    ('Books & Media'),
    ('Collectibles'),
    ('Sports & Outdoors'),
    ('Automotive'),
    ('Health & Beauty'),
    ('Crafts & DIY'),
    ('Business & Industrial'),
    ('Hobbies'),
    ('Musical Instruments'),
    ('Art'),
    ('Pets');
