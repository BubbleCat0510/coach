/*
 Navicat Premium Dump SQL

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80045 (8.0.45)
 Source Host           : localhost:3306
 Source Schema         : champion_coach

 Target Server Type    : MySQL
 Target Server Version : 80045 (8.0.45)
 File Encoding         : 65001

 Date: 28/04/2026 10:48:15
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for coach_exam_report
-- ----------------------------
DROP TABLE IF EXISTS `coach_exam_report`;
CREATE TABLE `coach_exam_report`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  `exam_session_id` bigint NOT NULL COMMENT '测试会话ID',
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '综合能力总结',
  `strengths` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '优势能力',
  `weaknesses` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '短板能力',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '测试总结报告表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_exam_round
-- ----------------------------
DROP TABLE IF EXISTS `coach_exam_round`;
CREATE TABLE `coach_exam_round`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `exam_session_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `round_no` int NOT NULL,
  `dimension` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ai_question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `answer_analysis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `ai_reply` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `user_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `round_score` int NULL DEFAULT 0,
  `scenario` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `exam_session_id`(`exam_session_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_exam_round_session` FOREIGN KEY (`exam_session_id`) REFERENCES `coach_exam_session` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 147 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_exam_score
-- ----------------------------
DROP TABLE IF EXISTS `coach_exam_score`;
CREATE TABLE `coach_exam_score`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '评分ID',
  `exam_session_id` bigint NOT NULL COMMENT '测试会话ID',
  `dimension` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '能力维度',
  `score` int NOT NULL COMMENT '维度得分（0–100）',
  `comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '评估评语',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '测试评分表（维度级）' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_exam_session
-- ----------------------------
DROP TABLE IF EXISTS `coach_exam_session`;
CREATE TABLE `coach_exam_session`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NULL DEFAULT NULL COMMENT '用户ID',
  `exam_mode` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '测试模式（专项/综合/模拟）',
  `status` tinyint NULL DEFAULT NULL COMMENT '1进行中/2已结束/3已评分',
  `total_score` int NULL DEFAULT NULL COMMENT '总分（评分后生成）',
  `exam_rules` json NULL COMMENT '测试规则快照',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `finish_time` datetime NULL DEFAULT NULL COMMENT '测试结束时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_exam_session_user` FOREIGN KEY (`user_id`) REFERENCES `coach_user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 44 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_file_upload
-- ----------------------------
DROP TABLE IF EXISTS `coach_file_upload`;
CREATE TABLE `coach_file_upload`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '文件ID',
  `user_id` bigint NOT NULL COMMENT '上传用户ID',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件名',
  `file_path` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件路径',
  `file_size` bigint NOT NULL COMMENT '文件大小（字节）',
  `file_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件类型',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'other' COMMENT '文件分类：technical=技术文档, training=培训资料, other=其他',
  `file_hash` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件哈希值（用于去重）',
  `status` tinyint NULL DEFAULT 1 COMMENT '状态：1 正常 / 0 禁用',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `create_time`(`create_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '文件上传表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for coach_question_bank
-- ----------------------------
DROP TABLE IF EXISTS `coach_question_bank`;
CREATE TABLE `coach_question_bank`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `options` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'single',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'medium',
  `status` tinyint NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_category`(`category` ASC) USING BTREE,
  INDEX `idx_type`(`type` ASC) USING BTREE,
  INDEX `idx_difficulty`(`difficulty` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_train_round
-- ----------------------------
DROP TABLE IF EXISTS `coach_train_round`;
CREATE TABLE `coach_train_round`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '轮次 ID',
  `session_id` bigint NOT NULL COMMENT '训练会话 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `ai_question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'AI 提问',
  `user_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户回答',
  `ai_reply` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'AI 教练回复',
  `score` int NULL DEFAULT NULL COMMENT '训练评分',
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '改进建议',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `fk_train_round_session`(`session_id` ASC) USING BTREE,
  CONSTRAINT `fk_train_round_session` FOREIGN KEY (`session_id`) REFERENCES `coach_train_session` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 45 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '训练轮次表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_train_session
-- ----------------------------
DROP TABLE IF EXISTS `coach_train_session`;
CREATE TABLE `coach_train_session`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '训练会话 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '训练主题',
  `role_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'AI 教练角色',
  `status` tinyint NULL DEFAULT 1 COMMENT '1 进行中 / 2 已完成',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_train_session_user` FOREIGN KEY (`user_id`) REFERENCES `coach_user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '训练会话表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_user
-- ----------------------------
DROP TABLE IF EXISTS `coach_user`;
CREATE TABLE `coach_user`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户唯一 ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '登录账号',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '登录密码（哈希）',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '昵称',
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '岗位 / 角色',
  `status` tinyint NULL DEFAULT 1 COMMENT '状态：1 正常 / 0 禁用',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coach_user_file_progress
-- ----------------------------
DROP TABLE IF EXISTS `coach_user_file_progress`;
CREATE TABLE `coach_user_file_progress`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `file_id` bigint NOT NULL COMMENT '???ID',
  `progress` int NOT NULL DEFAULT 0 COMMENT '阅读进度（0-100）',
  `last_read_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后阅读时间',
  `is_completed` tinyint NOT NULL DEFAULT 0 COMMENT '是否完成：0否/1是',
  `total_learning_time` int NOT NULL DEFAULT 0 COMMENT '????????????',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_file_unique`(`user_id` ASC, `file_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `ile_id`(`file_id` ASC) USING BTREE,
  INDEX `last_read_time`(`last_read_time` ASC) USING BTREE,
  INDEX `file_id`(`file_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户文件学习进度表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for round_answer
-- ----------------------------
DROP TABLE IF EXISTS `round_answer`;
CREATE TABLE `round_answer`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '测试轮次ID',
  `exam_session_id` bigint NOT NULL COMMENT '测试会话ID',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `round_no` int NOT NULL COMMENT '第几轮',
  `dimension` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '能力维度',
  `ai_question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'AI考题',
  `answer_analysis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '答案解析（AI生成）',
  `ai_reply` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '标准答案（AI生成）',
  `user_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户回答',
  `round_score` int NULL DEFAULT NULL COMMENT '单轮题目得分（如2/4/10/0）',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '测试中每一轮的原始作答' ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for v_user_learning_activity
-- ----------------------------
DROP VIEW IF EXISTS `v_user_learning_activity`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_user_learning_activity` AS select ('exam' collate utf8mb4_0900_ai_ci) AS `activity_type`,`s`.`id` AS `session_id`,`s`.`user_id` AS `user_id`,(`u`.`nickname` collate utf8mb4_0900_ai_ci) AS `user_name`,`s`.`create_time` AS `start_time`,`s`.`finish_time` AS `end_time`,`s`.`total_score` AS `score`,`s`.`status` AS `status`,(concat('考试-',ifnull(`s`.`exam_mode`,'未知模式')) collate utf8mb4_0900_ai_ci) AS `title`,(select count(0) from `coach_exam_round` `r` where (`r`.`exam_session_id` = `s`.`id`)) AS `round_count` from (`coach_exam_session` `s` left join `coach_user` `u` on((`s`.`user_id` = `u`.`id`))) union all select 'train' AS `train`,`ts`.`id` AS `id`,`ts`.`user_id` AS `user_id`,(`u`.`nickname` collate utf8mb4_0900_ai_ci) AS `u.nickname COLLATE utf8mb4_0900_ai_ci`,`ts`.`create_time` AS `create_time`,`ts`.`update_time` AS `update_time`,NULL AS `NULL`,`ts`.`status` AS `status`,(concat('训练-',ifnull(`ts`.`title`,'未命名主题')) collate utf8mb4_0900_ai_ci) AS `Name_exp_19`,(select count(0) from `coach_train_round` `tr` where (`tr`.`session_id` = `ts`.`id`)) AS `Name_exp_20` from (`coach_train_session` `ts` left join `coach_user` `u` on((`ts`.`user_id` = `u`.`id`))) order by `start_time` desc;

SET FOREIGN_KEY_CHECKS = 1;
