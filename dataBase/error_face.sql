--=============================================================================================================
-- 创建数据库
CREATE DATABASE IF NOT EXISTS `recordDB`;

--错误数据信息表error_record_table:
DROP TABLE IF EXISTS `error_record_table`;          
CREATE TABLE IF NOT EXISTS `error_record_table`
(
  "error_id" integer NOT NULL PRIMARY KEY autoincrement,
  "error_time" TimeStamp NOT NULL DEFAULT (datetime('now','localtime')),
  "error_type" integer(1) NOT NULL
);
-- 1表示带口罩被识别未没带口罩, 0表示没带口罩被识别为带口罩
--INSERT INTO error_record_table(error_type) values (0);