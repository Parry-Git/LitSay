-- 启用外键支持
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 用户表
-- ----------------------------
CREATE TABLE `user`
(
    `user_id`       INT AUTO_INCREMENT PRIMARY KEY,
    `user_name`     VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role`          TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '0=user, 1=admin'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 目录表 (含闭包表模型)
-- ----------------------------
CREATE TABLE `directory`
(
    `directory_id`   INT AUTO_INCREMENT PRIMARY KEY,
    `user_id`        INT          NOT NULL,
    `parent_id`      INT       DEFAULT NULL,
    `directory_name` VARCHAR(255) NOT NULL,
    `create_time`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_directory` (`user_id`, `directory_name`, `parent_id`), -- 同一父目录下不允许重名
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`parent_id`)
        REFERENCES `directory` (`directory_id`)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- 目录闭包表
CREATE TABLE `directory_closure`
(
    `ancestor_id`   INT NOT NULL,
    `descendant_id` INT NOT NULL,
    `depth`         INT NOT NULL,
    `user_id`       INT NOT NULL,
    PRIMARY KEY (`ancestor_id`, `descendant_id`),
    FOREIGN KEY (`ancestor_id`)
        REFERENCES `directory` (`directory_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`descendant_id`)
        REFERENCES `directory` (`directory_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 会议/期刊表
-- ----------------------------
CREATE TABLE `container`
(
    `container_id`        INT AUTO_INCREMENT PRIMARY KEY,
    `user_id`             INT                            NOT NULL,
    `type`                ENUM ('conference', 'journal') NOT NULL,
    `container_name`      VARCHAR(255)                   NOT NULL,
    `conference_time`     TIMESTAMP                      NULL DEFAULT NULL,
    `conference_location` VARCHAR(255)                        DEFAULT NULL,
    `journal_issue`       VARCHAR(255)                        DEFAULT NULL,
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    -- 校验字段合法性
    CHECK (
        (`type` = 'conference' AND `conference_time` IS NOT NULL) OR
        (`type` = 'journal' AND `journal_issue` IS NOT NULL)
        )
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 论文表
-- ----------------------------
CREATE TABLE `document`
(
    `document_id`      INT AUTO_INCREMENT PRIMARY KEY,
    `directory_id`     INT           NOT NULL,
    `container_id`     INT                DEFAULT NULL,
    `user_id`          INT           NOT NULL,
    `title`            VARCHAR(255)  NOT NULL,
    `doi`              VARCHAR(40)        DEFAULT NULL,
    `local_url`        VARCHAR(1024) NOT NULL,
    `publication_date` TIMESTAMP     NULL DEFAULT NULL,
    `create_time`      TIMESTAMP          DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`directory_id`)
        REFERENCES `directory` (`directory_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`container_id`)
        REFERENCES `container` (`container_id`)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 作者表
-- ----------------------------
CREATE TABLE `author`
(
    `author_id`    INT AUTO_INCREMENT PRIMARY KEY,
    `user_id`      INT          NOT NULL,
    `author_name`  VARCHAR(255) NOT NULL,
    `author_email` VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 单位表
-- ----------------------------
CREATE TABLE `institution`
(
    `institution_id`       INT AUTO_INCREMENT PRIMARY KEY,
    `user_id`              INT          NOT NULL,
    `institution_name`     VARCHAR(255) NOT NULL,
    `institution_location` VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 关键词表
-- ----------------------------
CREATE TABLE `keyword`
(
    `keyword_id`   INT AUTO_INCREMENT PRIMARY KEY,
    `user_id`      INT          NOT NULL,
    `keyword_name` VARCHAR(255) NOT NULL,
    UNIQUE KEY `uq_keyword` (`user_id`, `keyword_name`), -- 同一用户下关键词不重复
    FOREIGN KEY (`user_id`)
        REFERENCES `user` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- 关联关系表
-- ----------------------------
-- 论文-作者关系
CREATE TABLE `document_author`
(
    `document_id` INT NOT NULL,
    `author_id`   INT NOT NULL,
    `sequence`    INT NOT NULL COMMENT '作者顺序',
    PRIMARY KEY (`document_id`, `author_id`),
    FOREIGN KEY (`document_id`)
        REFERENCES `document` (`document_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`author_id`)
        REFERENCES `author` (`author_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- 论文-关键词关系
CREATE TABLE `document_keyword`
(
    `document_id` INT NOT NULL,
    `keyword_id`  INT NOT NULL,
    PRIMARY KEY (`document_id`, `keyword_id`),
    FOREIGN KEY (`document_id`)
        REFERENCES `document` (`document_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`keyword_id`)
        REFERENCES `keyword` (`keyword_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- 作者-单位关系
CREATE TABLE `author_institution`
(
    `author_id`      INT NOT NULL,
    `institution_id` INT NOT NULL,
    PRIMARY KEY (`author_id`, `institution_id`),
    FOREIGN KEY (`author_id`)
        REFERENCES `author` (`author_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`institution_id`)
        REFERENCES `institution` (`institution_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

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