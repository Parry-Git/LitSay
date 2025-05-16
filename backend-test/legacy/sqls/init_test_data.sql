-- 禁用外键检查（可选，MySQL特有）
SET FOREIGN_KEY_CHECKS = 0;

-- 按依赖关系删除表
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS papers;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;


-- 创建文献表
CREATE TABLE IF NOT EXISTS papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    authors VARCHAR(255) NOT NULL,
    abstract TEXT,
    publish_date DATE,
    keywords VARCHAR(255),
    pdf_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role ENUM('admin', 'researcher', 'student') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建收藏表
CREATE TABLE IF NOT EXISTS favorites (
    user_id INT NOT NULL,
    paper_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, paper_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- 插入示例文献数据
INSERT INTO papers (title, authors, abstract, publish_date, keywords, pdf_url) VALUES
('深度学习在图像识别中的应用', '张伟,李娜', '本文探讨了深度学习技术在计算机视觉领域的最新进展...', '2023-01-15', '深度学习,计算机视觉', '/pdfs/dl_vision.pdf'),
('量子计算研究综述', '王强,赵敏', '全面回顾了量子计算的发展历程和当前研究热点...', '2022-11-20', '量子计算,量子算法', '/pdfs/quantum_computing.pdf'),
('区块链技术的安全挑战', '陈明,刘芳', '分析了区块链系统面临的主要安全威胁和防御策略...', '2023-03-05', '区块链,网络安全', '/pdfs/blockchain_security.pdf'),
('自然语言处理中的预训练模型', '周杰,吴婷', '系统比较了BERT、GPT等预训练语言模型的优缺点...', '2023-02-10', 'NLP,预训练模型', '/pdfs/pretrain_models.pdf'),
('边缘计算与物联网', '郑浩,孙丽', '研究了边缘计算在物联网场景下的应用和优化方法...', '2022-12-25', '边缘计算,IoT', '/pdfs/edge_computing.pdf');

-- 插入示例用户数据
INSERT INTO users (username, password, email, role) VALUES
('admin', 'admin123', 'admin@example.com', 'admin'),
('researcher1', 'res123', 'researcher1@example.com', 'researcher'),
('student1', 'stu123', 'student1@example.com', 'student'),
('student2', 'stu456', 'student2@example.com', 'student');

-- 插入收藏关系
INSERT INTO favorites (user_id, paper_id) VALUES
(2, 1),
(2, 3),
(3, 2),
(3, 4),
(4, 1),
(4, 5);