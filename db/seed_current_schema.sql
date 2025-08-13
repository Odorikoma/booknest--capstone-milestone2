SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 清空表（按外键依赖顺序）
DROP TABLE IF EXISTS borrows;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- 创建 users 表
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('user','admin') NOT NULL DEFAULT 'user',
  create_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建 books 表
CREATE TABLE books (
  id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  description TEXT NULL,
  cover_image_url VARCHAR(255) NULL,
  stock INT UNSIGNED NOT NULL DEFAULT 0,
  price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建 borrows 表
CREATE TABLE borrows (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  borrow_date TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  return_date TIMESTAMP NULL DEFAULT NULL,
  borrow_status ENUM('borrowed','returned','requested','denied','approved') NOT NULL DEFAULT 'requested',
  notes TEXT NULL,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  KEY book_id (book_id),
  CONSTRAINT borrows_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT borrows_ibfk_2 FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入 users（密码是 123456 / admin / 123456 的哈希）
INSERT INTO users (id, username, email, password_hash, role, create_at) VALUES
  (3, '测试用户', 'test@ex.com', '$pbkdf2-sha256$29000$8P7f29Zj2Ud3rDcqP.3WDA$7YvHRihBsu/1ci2v2snLVQho9oJfgWkC4UmVHt.Lqp8', 'user', '2025-07-25 08:53:52'),
  (4, 'admin',   'admin@ex.com', '$pbkdf2-sha256$29000$pi19dA6uRG9cWv5n3fquzA$aTK3nbeGZ3vbzTSv3rF7Dp5gQ5ZK3GfO9mmlGQJ6m3M',  'admin','2025-07-26 09:12:57'),
  (5, 'testuser','test@example.com', '$pbkdf2-sha256$29000$8P7f29Zj2Ud3rDcqP.3WDA$7YvHRihBsu/1ci2v2snLVQho9oJfgWkC4UmVHt.Lqp8', 'user','2025-07-26 12:25:08');

-- 插入 books
INSERT INTO books (id, title, author, description, stock, cover_image_url, price, created_at) VALUES
  (1, 'Python 编程', '张三', 'Python 入门教程', 13, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTGuZ0mDCP3I9AftJmiC5t8A3xxCoMGZRicNQ&s', 0.00, '2025-07-25 09:00:53'),
  (3, '挺好听任何', '3434', '规划法规和', 343, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTGuZ0mDCP3I9AftJmiC5t8A3xxCoMGZRicNQ&s', 0.00, '2025-07-26 10:28:55');

-- 插入 borrows
INSERT INTO borrows (id, user_id, book_id, borrow_date, return_date, borrow_status, notes) VALUES
  (1, 3, 1, '2025-07-25 09:02:12', NULL, 'denied', NULL),
  (2, 3, 1, '2025-07-26 09:39:36', '2025-07-26 10:05:53', 'returned', NULL),
  (3, 3, 3, '2025-07-26 11:00:10', NULL, 'requested', NULL),
  (4, 3, 3, '2025-07-31 00:00:00', NULL, 'requested', NULL);

SET FOREIGN_KEY_CHECKS = 1;
