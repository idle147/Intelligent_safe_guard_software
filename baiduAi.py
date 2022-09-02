# -*- coding: utf-8 -*-
from Global import CONFIG
from aip import AipBodyAnalysis
from aip import AipFace


class CFaceId(object):
    def __init__(self, group_default='temp'):
        "输入APP_ID的值"
        self.APP_ID = CONFIG["@baidu_api"]["APP_ID"]
        "输入KEY的值"
        self.API_KEY = CONFIG["@baidu_api"]["API_KEY"]
        "输入SECRET_KEY的值"
        self.SECRET_KEY = CONFIG["@baidu_api"]["SECRET_KEY"]
        self.aipFace = AipFace(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.bodyCheck = AipBodyAnalysis(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.photo_name = ''
        self.group = group_default

    def getUser(self, user_id, group_id):
        """
        获取用户的名称
        :param user_id: 用户ID
        :param group_id: 群组ID
        :return:用户名的结果,返回给上层封装进行处理
        """
        return self.aipFace.getUser(user_id, group_id)

    def GroupAdd(self, group_name):
        """
        创建组用户
        :param group_name:组名
        :return: 创建的结果返回给上层防撞进行处理
        """
        return self.aipFace.groupAdd(group_name)

    def FaceAdd(self, image, user_id, group_id='temp'):
        """
        添加人脸
        :param image: 人脸图像base64
        :param user_id: 用户ID
        :param group_id: 组名, 默认为temp
        :return: 返回添加后的结果
        """
        return self.aipFace.addUser(image, "BASE64", group_id, user_id)

    def FaceUpdate(self, image, user_id, group_id='temp'):
        """
        更新人脸
        :param image:人脸图像 base64
        :param user_id: 用户ID
        :param group_id: 组名, 默认为temp
        :return: 返回更新后的结果
        """
        return self.aipFace.addUser(image, "BASE64", group_id, user_id)

    def FaceSearch(self, image, image_type="BASE64", group_id="temp"):
        """
        脸部搜索
        :param image: 图像的编码
        :param image_type: BASE-64
        :param group_id: 群组ID，默认为temp
        :return:
        """
        # image 为base64字符串
        options = {
            "match_threshold": 75,
            "liveness_control": "NORMAL",
            "quality_control": "NORMAL"
        }
        return self.aipFace.search(image, image_type, group_id)

    def FaceMultiSearch(self, image, image_type="BASE64", group_id="temp"):
        """
        1张图片多个脸部搜索
        :param image:
        :param image_type:
        :param group_id:
        :return:获取的结果
        """
        # image 为base64字符串
        options = {
            "max_face_num": 10,
            "quality_control": "NORMAL"
        }
        return self.aipFace.multiSearch(image, image_type, group_id, options)

    def GetUser(self, uid, group='temp'):
        """
        获取用户名
        :param uid:  用户ID
        :param group: 组ID
        :return: 获取的结果
        """
        result = self.aipFace.getUser(uid, group)
        print(result)

    def GetGroup(self, start=0, num=100):
        """
        获取组内的组列表
        :param start: 其实位置
        :param num:数量
        :return:结果
        """
        options = {
            'start': start,
            'num': num
        }
        result = self.aipFace.getGroupList(options)
        print(result)

    def GetGroupUser(self, group='temp', start=0, num=100):
        """
        获取组内用户列表
        :param group: 组名
        :param start: 起始名
        :param num: 终止名
        :return: 返回值
        """
        options = {
            'start': start,
            'num': num
        }
        return self.aipFace.getGroupUsers(group, options)

    def DelUser(self, uid):
        """
        删除用户
        :param uid:用户ID
        :return:删除的结果
        """
        return self.aipFace.deleteUser(uid)

    def BodyTracking(self, image, is_init, area):
        """
        身体追踪
        :param image: 图像信息
        :param is_init: 初始化信心
        :param area: 定位的区域
        :return: 追踪的结果
        """
        dynamic = "true"
        options = {"case_id": 1, "case_init": is_init, "area": area}
        return self.bodyCheck.bodyTracking(image, dynamic, options)
