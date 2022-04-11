# 智能校园防御软件

### 版权说明
本项目为个人练手项目，项目内的图片素材均来源网上，代码均为本人手写，仅供参考，请勿用于商业用途。本项目模型训练素材采用 网络爬虫获取，可能涉及版权问题，不予公开，请自行训练。

### 环境选型
1. 语言：Python
2. 操作系统：Windows
3. 数据库：MySQL
4. 窗口界面：PyQT
5. API接口：百度AI接口，用以实现人脸登陆与注册

### 远程MySQL表结构
**本源码的远端MYSQL服务器过期了，上面的mysql数据库也凉凉了，在这里更新远程mysql表结构，有兴趣的可以自己搭建一下**
![QQ图片20220411225513](https://user-images.githubusercontent.com/56959230/162767175-5ad4cb7d-9231-4a1a-811c-90d46197b5f3.png)

### 远程表结构sql脚本（未测试）
```
DROP TABLE IF EXISTS `access_record_table`;
CREATE TABLE `access_record_table` (
  record_id int(11) NOT NULL AUTO_INCREMENT  COMMENT '主键',
  has_mask enum('0','1') NOT NULL DEFAULT '0' COMMENT '是否佩戴口罩',
  access_time timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  place_id int(11) UNSIGNED NOT NULL DEFAULT '00000' COMMENT '设备id',
  stu_id int(1) int(11)  UNSIGNED NOT NULL DEFAULT '00000' COMMENT '学生id',
  PRIMARY KEY (record_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `place_table`;
CREATE TABLE `place_table` (
  place_id int,
  place_name varchar(32) DEFAULT NULL COMMENT '地点名字',
  place_time timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  foreign key(place_id) references access_record_table(place_id) on delete cascade on update cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `stu_table`;
CREATE TABLE `stu_table` (
  stu_id int,
  stu_name varchar(32) DEFAULT NULL COMMENT '学生名字',
  stu_status enum('0','1','2') NOT NULL DEFAULT '0' COMMENT '学生状态',
  stu_times timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  foreign key(stu_id) references access_record_table(stu_id) on delete cascade on update cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `usr_table`;
CREATE TABLE `usr_table` (
  stu_id int(11) NOT NULL AUTO_INCREMENT  COMMENT '主键',
  usr_name varchar(32) DEFAULT NULL COMMENT '用户名称',
  usr_pic varchar(32) DEFAULT NULL COMMENT '用户图片名称',
  usr_times timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  PRIMARY KEY (stu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
```

### 项目背景
智能校园防御软件是实现了一款基于摄像头数据采集、人脸识别、口罩识别、 数据统计的预警系统，该种防御系统能够通过人脸识别进行管理员登录打卡，通过安装在教室内的固定摄像头，实时采集教室内上课同学的图像，判断是否有带口罩，从而在监控屏幕中予以标记提示警卫人员。采用 OpenCV/爬虫数据采集、利用 Numpy、Pandas 及特征工程、模型聚合进行数据预处理、CNN 模型训练框架。

### 用例图功能概述
![image](https://user-images.githubusercontent.com/56959230/132306918-949ff85f-5851-4b7d-93c2-d76ada0d9367.png)

### 项目系统框架MVC说明——输入
![image](https://user-images.githubusercontent.com/56959230/132306673-71058254-bda7-4ebf-a2fa-b159d8ec9b8c.png)

### 项目系统框架MVC说明——反馈
![image](https://user-images.githubusercontent.com/56959230/132306771-d4930fdb-daaa-4a38-bd01-c0247d1fdbb6.png)

### 联系方式
本项目为本人练手项目，请勿商用，若有问题请自行解决。实在无法解决的，请将问题发送邮件至：2827709585@qq.com
（看到就会回复）

**最后更新时间：2022.04.11**
