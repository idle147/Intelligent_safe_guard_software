import base64
import cv2
from baiduAi import *


class CAiFaceDetection():
    def __init__(self):
        """
            构造函数: 判断连接, 判断相应组的建立
        """
        self.face = CFaceId()
        try:
            self.CreatGroup()
        except:
            print("网络连接出错")

    def UserQuire(self, user_id, group_id):
        """
        用户信息查询
        :param user_id: 用户ID
        :param group_id: 组ID
        :return: 查询的结果
        """
        result = self.face.getUser(user_id, group_id)
        if result['error_msg'] == 'SUCCESS':
            return '0'  # 查有相同的用户名
        elif result['error_msg'] == 'user not exist':
            return '1'  # 查无相同的用户名
        else:
            return "Connect Error!"

    def CreatGroup(self):
        """
        创建用户组: temp(学员用户组)/ safeguard(安保用户组)
        :return:
        """
        self.face.GroupAdd("SafeGuard")
        self.face.GroupAdd("temp")

    def FaceAdd(self, name, image, group="temp"):
        """
        人脸添加
        :param name: 人脸的名称
        :param image: 图片的名称
        :param group: 组的名称
        :return: 添加的结果
        """
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = str(base64.b64encode(img_encode))[2:-1]
        result = self.face.FaceAdd(image_code, name, group)
        if result['error_msg'] == 'SUCCESS':
            return result['result']["face_token"]
        return False

    def GetFaceToken(self, user_id):
        """
        获取脸照片的唯一标识符
        :param user_id: 用户ID
        :return: 唯一标识符集合
        """
        result = self.face.aipFace.faceGetlist(user_id, self.face.group)
        if result['error_code'] == 0:
            return result['result']['face_list'][0]['face_token']
        else:
            return False

    def FaceUpdate(self, name, image):
        """
        脸部更新
        :param name: 用户脸部名称
        :param image: 用户图像
        :return: 脸部更新的结果
        """
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = str(base64.b64encode(img_encode))[2:-1]
        result = self.face.FaceUpdate(image_code, name, self.face.group)
        if result['error_msg'] == 'SUCCESS':
            return result['result']["face_token"]
        return False

    def FaceDelete(self, user_id, face_token):
        """
        脸部删除
        :param user_id: 用户ID
        :param face_token: 人脸标识符
        :return: 删除的结果
        """
        result = self.face.aipFace.faceDelete(user_id, self.face.group, face_token)
        if result['error_code'] == 0:
            return True
        else:
            return False

    def FaceResearch(self, image, group_name="temp"):
        """
        人脸搜索匹配
        :param image: 脸部的图像 Base64编码
        :param group_name: 组名
        :return:
        """
        local = []
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = str(base64.b64encode(img_encode))[2:-1]
        result = self.face.FaceMultiSearch(image_code, "BASE64", group_name)
        if result['error_msg'] == 'SUCCESS':
            for ret in result['result']['face_list']:
                if len(ret['user_list']) != 0:
                    local.append((ret['location'], 'green'))
                else:
                    local.append((ret['location'], 'red'))
        return local

    def FaceLogin(self, image, group_name="temp"):
        """
        人脸登陆
        :param image: 脸部的图片
        :param group_name: 组名
        :return: 登陆的结果
        """
        local = []
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = str(base64.b64encode(img_encode))[2:-1]
        result = self.face.FaceMultiSearch(image_code, "BASE64", group_name)
        if result['error_msg'] == 'SUCCESS':
            local = result['result']['face_list'][0]['user_list'][0]['user_id']
        return local

    def FaceCheck(self, frame_img, group_name="temp"):
        """
        脸部查验
        :param frame_img: 帧图片
        :param group_name: 组名
        :return: 人脸识别的结果
        """
        local = self.FaceResearch(frame_img, group_name)
        # 对每张人脸进行识别
        for x in range(len(local)):
            width = int(local[x][0]['width'])
            height = int(local[x][0]['height'])
            left = int(local[x][0]['left'])
            top = int(local[x][0]['top'])
            if local[x][1] == 'green':
                cv2.rectangle(frame_img, (left, top - width), (left + height, top + width), (0, 255, 0), 2)
            else:
                cv2.rectangle(frame_img, (left, top - width), (left + height, top + width), (0, 0, 255), 2)
        return frame_img

    def AiBodyTracking(self, image, is_init):
        """
        AI身体追踪
        :param image: 人脸图片 Base64
        :param is_init: 初始化
        :return: 识别的结果
        """
        area = str(image.shape[0]) + ',' + str(image.shape[1])
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = base64.b64encode(img_encode)[2:-1]
        result = self.face.BodyTracking(image_code, is_init, area)
        print(result)

    # 1：M对比
    def FaceCompare(self, image, group_id):
        """
        人脸对比的结果
        :param image: 人脸图片 Base64
        :param group_id: 组ID
        :return: 人脸对比的结果
        """
        img_encode = cv2.imencode('.jpg', image)[1]
        image_code = str(base64.b64encode(img_encode))[2:-1]
        result = self.face.FaceSearch(image_code, group_id=group_id)
        if result['error_msg'] == 'SUCCESS' and result['result']['user_list']["score"] > 80:
            return result['result']['user_id'], result['result']['user_info']
        return None, None

    # 用户信息查询
    def UserIdQuire(self, user_id, group_id='temp'):
        """
        用户信息查询, 判断是否存在该用户ID
        :param user_id: 用户ID
        :param group_id: 组ID
        :return: 查询的结果
        """
        result = self.face.UserQuire(user_id, group_id=group_id)
        return result
