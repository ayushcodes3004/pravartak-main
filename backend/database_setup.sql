CREATE DATABASE IF NOT EXISTS pravartak;
USE pravartak;

CREATE TABLE IF NOT EXISTS mentors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    expertise VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    roll_no VARCHAR(20),
    gender VARCHAR(10),
    category VARCHAR(50),
    fees_status VARCHAR(20),
    attendance FLOAT,
    marks FLOAT,
    backlog INT,
    dropout_risk BOOLEAN DEFAULT FALSE,
    mentor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES mentors(id)
);