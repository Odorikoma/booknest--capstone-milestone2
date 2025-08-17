-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ===================================================================
-- 1. 创建数据库
-- ===================================================================
CREATE DATABASE IF NOT EXISTS `booknest` 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_0900_ai_ci;

USE `booknest`;

-- ===================================================================
-- 2. 创建用户表 (users)
-- ===================================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
    `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '邮箱',
    `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码哈希',
    `role` enum('user','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'user' COMMENT '用户角色',
    `create_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY `email` (`email`) USING BTREE,
    UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';

-- ===================================================================
-- 3. 创建图书表 (books)
-- ===================================================================
DROP TABLE IF EXISTS `books`;
CREATE TABLE `books` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '图书ID',
    `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '书名',
    `author` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '作者',
    `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '描述',
    `stock` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '库存数量',
    `cover_image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '封面图片URL',
    `price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '价格',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `idx_title` (`title`) USING BTREE,
    INDEX `idx_author` (`author`) USING BTREE,
    INDEX `idx_created_at` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='图书表';

-- ===================================================================
-- 4. 创建借阅记录表 (borrows)
-- ===================================================================
DROP TABLE IF EXISTS `borrows`;
CREATE TABLE `borrows` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '借阅记录ID',
    `user_id` int NOT NULL COMMENT '用户ID',
    `book_id` int NOT NULL COMMENT '图书ID',
    `borrow_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '借阅日期',
    `return_date` timestamp NULL DEFAULT NULL COMMENT '归还日期',
    `borrow_status` enum('requested','borrowed','returned','denied') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'requested' COMMENT '借阅状态',
    `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    INDEX `idx_user_id` (`user_id`) USING BTREE,
    INDEX `idx_book_id` (`book_id`) USING BTREE,
    INDEX `idx_borrow_status` (`borrow_status`) USING BTREE,
    INDEX `idx_borrow_date` (`borrow_date`) USING BTREE,
    CONSTRAINT `fk_borrows_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_borrows_book_id` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARACTER SET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='借阅记录表';

-- ===================================================================
-- 5. 插入初始数据
-- ===================================================================

INSERT INTO `users` (`username`, `email`, `password_hash`, `role`) VALUES 
('admin', 'admin@booknest.com', 'pbkdf2:sha256:600000$randomsalt1$5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 'admin'),
('testuser', 'test@booknest.com', 'pbkdf2:sha256:600000$randomsalt2$5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 'user');

INSERT INTO `books` (`title`, `author`, `description`, `stock`, `cover_image_url`, `price`) VALUES 
('Python编程从入门到实践', '埃里克·马瑟斯', 'Python编程入门经典教程，适合初学者学习', 5, 'https://picsum.photos/300/400?random=1', 89.00),
('JavaScript高级程序设计', '尼古拉斯·泽卡斯', 'JavaScript开发者必读经典，深入讲解JavaScript核心概念', 3, 'https://picsum.photos/300/400?random=2', 99.00),
('算法导论', 'Thomas H. Cormen', '计算机科学经典教材，全面介绍算法设计与分析', 2, 'https://picsum.photos/300/400?random=3', 128.00),
('深入理解计算机系统', 'Randal E. Bryant', '系统程序员必读，深入理解计算机系统原理', 4, 'https://picsum.photos/300/400?random=4', 139.00),
('设计模式', 'Erich Gamma', '面向对象设计经典，23种设计模式详解', 6, 'https://picsum.photos/300/400?random=5', 79.00);

-- 插入示例借阅记录
INSERT INTO `borrows` (`user_id`, `book_id`, `borrow_status`, `notes`) VALUES 
(2, 1, 'borrowed', '学习Python编程'),
(2, 2, 'requested', '想学习JavaScript');

-- ===================================================================
-- 6. 重新开启外键检查
-- ===================================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ===================================================================
-- 7. 显示创建结果
-- ===================================================================
SHOW TABLES;

SELECT 'Database and tables created successfully!' as message;