-- 启用外键支持
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `author_institution`;
DROP TABLE IF EXISTS `document_keyword`;
DROP TABLE IF EXISTS `document_author`;
DROP TABLE IF EXISTS `keyword`;
DROP TABLE IF EXISTS `institution`;
DROP TABLE IF EXISTS `author`;
DROP TABLE IF EXISTS `document`;
DROP TABLE IF EXISTS `container`;
DROP TABLE IF EXISTS `directory_closure`;
DROP TABLE IF EXISTS `directory`;
DROP TABLE IF EXISTS `user`;

-- ----------------------------
-- 用户表
-- ----------------------------
CREATE TABLE `user` (
  `user_id`       INT AUTO_INCREMENT,
  `user_name`     VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role`          TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '0=user, 1=admin',
  CONSTRAINT `pk_user` PRIMARY KEY (`user_id`),
  CONSTRAINT `uq_user_name` UNIQUE KEY (`user_name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 目录表 (含闭包表模型)
-- ----------------------------
CREATE TABLE `directory` (
  `directory_id`   INT AUTO_INCREMENT,
  `user_id`        INT          NOT NULL,
  `parent_id`      INT                   DEFAULT NULL,
  `directory_name` VARCHAR(255) NOT NULL,
  `create_time`    TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `pk_directory` PRIMARY KEY (`directory_id`),
  CONSTRAINT `uq_directory_user_name_parent` UNIQUE KEY (`user_id`, `directory_name`, `parent_id`), -- 同一父目录下不允许重名
  CONSTRAINT `fk_directory_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_directory_parent` FOREIGN KEY (`parent_id`) REFERENCES `directory` (`directory_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 目录闭包表
CREATE TABLE `directory_closure` (
  `ancestor_id`   INT NOT NULL,
  `descendant_id` INT NOT NULL,
  `depth`         INT NOT NULL,
  `user_id`       INT NOT NULL,
  CONSTRAINT `pk_directory_closure` PRIMARY KEY (`ancestor_id`, `descendant_id`),
  CONSTRAINT `fk_closure_ancestor` FOREIGN KEY (`ancestor_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_closure_descendant` FOREIGN KEY (`descendant_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_closure_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 会议/期刊表
-- ----------------------------
CREATE TABLE `container` (
  `container_id`        INT AUTO_INCREMENT,
  `user_id`             INT                                NOT NULL,
  `type`                ENUM ('conference', 'journal')     NOT NULL,
  `container_name`      VARCHAR(255)                       NOT NULL,
  `conference_time`     TIMESTAMP                          NULL DEFAULT NULL,
  `conference_location` VARCHAR(255)                            DEFAULT NULL,
  `journal_issue`       VARCHAR(255)                            DEFAULT NULL,
  CONSTRAINT `pk_container` PRIMARY KEY (`container_id`),
  CONSTRAINT `fk_container_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE -- 移除原有约束条件，允许NULL值 (注: 此处user_id为NOT NULL, 该注释可能指之前版本)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 论文表
-- ----------------------------
CREATE TABLE `document` (
  `document_id`      INT(11) AUTO_INCREMENT,
  `directory_id`     INT(11)      NOT NULL,
  `container_id`     INT(11)               DEFAULT NULL,
  `user_id`          INT(11)      NOT NULL,
  `title`            VARCHAR(255) NOT NULL,
  `doi`              VARCHAR(40)           DEFAULT NULL,
  `local_url`        VARCHAR(1024)         DEFAULT NULL,
  `publication_date` TIMESTAMP             NULL DEFAULT NULL,
  `create_time`      TIMESTAMP             NULL DEFAULT CURRENT_TIMESTAMP,
  `stars`            INT(11)               DEFAULT NULL,
  `note`             TEXT                  DEFAULT NULL,
  CONSTRAINT `pk_document` PRIMARY KEY (`document_id`),
  CONSTRAINT `fk_document_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_document_directory` FOREIGN KEY (`directory_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_document_container` FOREIGN KEY (`container_id`) REFERENCES `container` (`container_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 作者表
-- ----------------------------
CREATE TABLE `author` (
  `author_id`    INT AUTO_INCREMENT,
  `user_id`      INT          NOT NULL,
  `author_name`  VARCHAR(255) NOT NULL,
  `author_email` VARCHAR(255)          DEFAULT NULL,
  CONSTRAINT `pk_author` PRIMARY KEY (`author_id`),
  CONSTRAINT `fk_author_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 单位表
-- ----------------------------
CREATE TABLE `institution` (
  `institution_id`       INT AUTO_INCREMENT,
  `user_id`              INT          NOT NULL,
  `institution_name`     VARCHAR(255) NOT NULL,
  `institution_location` VARCHAR(255)          DEFAULT NULL,
  CONSTRAINT `pk_institution` PRIMARY KEY (`institution_id`),
  CONSTRAINT `fk_institution_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 关键词表
-- ----------------------------
CREATE TABLE `keyword` (
  `keyword_id`   INT AUTO_INCREMENT,
  `user_id`      INT          NOT NULL,
  `keyword_name` VARCHAR(255) NOT NULL,
  CONSTRAINT `pk_keyword` PRIMARY KEY (`keyword_id`),
  CONSTRAINT `uq_keyword_user_name` UNIQUE KEY (`user_id`, `keyword_name`), -- 同一用户下关键词不重复
  CONSTRAINT `fk_keyword_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 关联关系表
-- ----------------------------
-- 论文-作者关系
CREATE TABLE `document_author` (
  `document_id` INT          NOT NULL,
  `author_id`   INT          NOT NULL,
  `sequence`    VARCHAR(255) NOT NULL COMMENT '作者顺序',
  CONSTRAINT `pk_document_author` PRIMARY KEY (`document_id`, `author_id`),
  CONSTRAINT `fk_docauthor_document` FOREIGN KEY (`document_id`) REFERENCES `document` (`document_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_docauthor_author` FOREIGN KEY (`author_id`) REFERENCES `author` (`author_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 论文-关键词关系
CREATE TABLE `document_keyword` (
  `document_id` INT NOT NULL,
  `keyword_id`  INT NOT NULL,
  CONSTRAINT `pk_document_keyword` PRIMARY KEY (`document_id`, `keyword_id`),
  CONSTRAINT `fk_dockeyword_document` FOREIGN KEY (`document_id`) REFERENCES `document` (`document_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dockeyword_keyword` FOREIGN KEY (`keyword_id`) REFERENCES `keyword` (`keyword_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 作者-单位关系
CREATE TABLE `author_institution` (
  `author_id`      INT NOT NULL,
  `institution_id` INT NOT NULL,
  CONSTRAINT `pk_author_institution` PRIMARY KEY (`author_id`, `institution_id`),
  CONSTRAINT `fk_authinst_author` FOREIGN KEY (`author_id`) REFERENCES `author` (`author_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_authinst_institution` FOREIGN KEY (`institution_id`) REFERENCES `institution` (`institution_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 索引
-- ----------------------------
CREATE INDEX `idx_document_user` ON `document` (`user_id`);
CREATE INDEX `idx_document_title` ON `document` (`title`);
CREATE INDEX `idx_document_doi` ON `document` (`doi`);
CREATE INDEX `idx_directory_user` ON `directory` (`user_id`);
CREATE INDEX `idx_closure_ancestor` ON `directory_closure` (`ancestor_id`);
CREATE INDEX `idx_closure_descendant` ON `directory_closure` (`descendant_id`);
CREATE INDEX `idx_keyword_user` ON `keyword` (`user_id`);
CREATE INDEX `idx_keyword_name` ON `keyword` (`keyword_name`);

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;