-- Ensure this script can be run multiple times (idempotent)
DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    authors VARCHAR(500),
    abstract TEXT,
    keywords VARCHAR(500),
    publication_year INT,
    user_id INT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Cascade delete if user is deleted
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional: Add some initial test data
-- INSERT INTO users (username, password_hash, email) VALUES ('testuser', 'hashed_password_for_testuser', 'test@example.com');
-- INSERT INTO papers (title, authors, user_id) VALUES ('Test Paper 1', 'Author A', 1);

-- Note: For OceanBase's MySQL mode, ENGINE=InnoDB and CHARSET=utf8mb4 are good defaults.