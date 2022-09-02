import datetime
import threading
import time
from PyQt5.QtGui import QImage, QPixmap
import cv2
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic.properties import QtWidgets


class CCamOpt():
    def __init__(self, save_dir, device_num, win_opt, face_check, mask_check):
        """
        相机类,初始化
        :param save_dir: 照片的存储位置
        :param device_num: 设备编号
        :param win_opt: 窗口类函数
        :param face_check: AI人脸检测类函数
        :param mask_check: 口罩识别类函数
        """
        self.save_dir = save_dir
        # 相关状态
        self.is_save = False
        self.is_start = False
        self.is_exit = False
        self.is_stop = False
        # 相关参数
        self.name = "temp"
        self.CAM_NUM = device_num
        self.save_res = False
        self.class_mode = False
        # 照片存储结构
        self.face_pic = []
        self.face_local = []
        # 相关类初始化
        self.c_win_opt = win_opt  # CWinOpt()
        self.face_check = face_check  # CAiFaceDetection()
        self.mask_check = mask_check  # CMaskDetection()
        # 口罩佩戴计数器
        self.mask_num = 0
        self.no_mask_num = 0

    def __del__(self):
        """
        析构函数, 调用退出相机函数
        :return: 无
        """
        self.ExitCam()

    def ThreadOptShowVideo(self, file_name, label, ai_switch=True, class_mode=False):
        """
        线程选项--将摄像机or视频显示到控件上面
        :param file_name: 文件名
        :param label: 标签
        :param ai_switch: 是否启动AI识别
        :param class_mode: 是否启动口罩事变
        :return: 无
        """
        # 创建线程
        if file_name != "":
            # 如果摄像头已经启动
            if self.is_start:
                if self.c_win_opt.TwoBtnMsgBox('警告', "请注意, 打开视频文件将会覆盖摄像头!", QMessageBox.Warning):
                    self.is_save = True
                else:
                    return
            # 如果摄像头未启动
            "打开视频文件"
            cap = cv2.VideoCapture(file_name)
            frame_all = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if frame_all <= 5:
                self.c_win_opt.OneBtnMsgBox('警告', "您打开的不是视频文件,或视频文件时常过短!", QMessageBox.Warning)
                return
        else:
            if self.is_start:
                if not self.c_win_opt.TwoBtnMsgBox(
                    '警告', "摄像头已经启动了, 是否重新启动?", QMessageBox.Warning
                ):
                    return
                self.SavePic()
                time.sleep(1)
            cap = cv2.VideoCapture()  # 视频流
            if flag := cap.open(self.CAM_NUM):
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            else:
                self.c_win_opt.OneBtnMsgBox('警告', "请检查相机于电脑是否连接正确!", QMessageBox.Warning)
                return
        # 标识符搁置
        self.is_exit = False
        # 判断是教室模式还是闸机模式
        self.ClassModeSet(class_mode)
        self.lock = threading.Lock()
        thread = threading.Thread(target=self.ShowVideo, args=(cap, label, ai_switch,))
        # 启动线程
        thread.start()

    def ClassModeSet(self, state):
        """
        分类模式设置
        :param state: False不启动口罩, True启动口罩
        :return:
        """
        self.class_mode = state

    def ReadSaveRes(self):
        """
        读取存储的结果
        :return: 无
        """
        return self.save_res

    def Stop(self):
        """
        暂停相机函数
        :return: 无
        """
        self.is_stop = True

    def Start(self):
        """
        启动相机函数
        :return: 无
        """
        self.is_stop = False

    def SavePic(self):
        """
        保存图片
        :return: 无
        """
        self.is_save = True

    def ExitCam(self):
        """
        退出相机
        :return: 无
        """
        self.is_save = True
        self.is_exit = True

    def GetFacePicInfo(self):
        """
        获取人脸相机的信息
        :return: 无
        """
        return self.face_pic, self.face_local

    def LabelSetPic(self, label, frame, width, height, draw_judge=False, save_staus=False):
        """
        标签设置, 将帧印到标签上
        :param label: QT标签控件
        :param frame: 视频帧
        :param width: 宽度
        :param height: 高度
        :param draw_judge: 是否需要调用AI, 绘制人脸框
        :param save_staus: 保存的状态
        :return: 返回的结果
        """
        frame = cv2.flip(frame, 1)  # 水平反转
        show = cv2.resize(frame, (width, height))  # 重设尺寸
        # 判断是否需要调用AI
        if draw_judge:
            self.face_check.FaceCheck(show)
        # 判断是否是教室检查模式
        elif self.class_mode:
            # 实时检查
            self.face_pic, self.face_local = self.mask_check.MaskDetect(show)
            if save_staus:
                for x in self.face_local:
                    if x[4] == 1:
                        self.mask_num += 1
                    elif x[4] == 0:
                        self.no_mask_num += 0
                    else:
                        continue
            # 时间追踪
            self.BodyTracking()
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 格式转换
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        try:
            label.setPixmap(QPixmap.fromImage(show_image))
        except:
            print("Labels设置出现错误:", label)
            return True
        # 如果点击保存则将该帧保存到目录里面
        if self.is_save or self.is_exit:
            print("结束视频帧的操作:", self.save_dir, self.name)
            self.save_res = True
            self.is_save = False
            self.is_start = False
            return True
        # 如果暂停, 则进入死循环
        while self.is_stop:
            pass

    def BodyTracking(self):
        """
        时间范围内判断
        :return: 无
        """
        # 范围时间
        time1 = '08:00'
        time2 = '12:00'
        time3 = '13:00'
        time4 = '18:00'
        time5 = '19:00'
        time6 = '22:00'
        # 获取当前时间
        now_time = datetime.datetime.now()
        hour = now_time.strftime('%H:%M')
        time = now_time.strftime('%Y-%m-%d %H:%M:%S')
        # 时间区间判断
        if hour == time1:
            self.mask_num = 0
            self.no_mask_num = 0
        elif hour == time2:
            # 保存到数据库
            self.DataSave(time, 1)
        elif hour == time3:
            self.mask_num = 0
            self.no_mask_num = 0
        elif hour == time4:
            # 保存到数据库
            self.DataSave(time, 2)
        elif hour == time5:
            self.mask_num = 0
            self.no_mask_num = 0
        elif hour == time6:
            # 保存到数据库
            self.DataSave(time, 3)

    # 保存到数据库内
    def DataSave(self, time, status):
        """
        数据保存
        :param time: 保存的时间点
        :param status: 保存的状态(1 8点, 2 16点, 3 22点)
        :return: 无
        """
        # 插入数据数据库
        z = [self.mask_num, self.no_mask_num, time, status]
        self.__c_sqlite_opt.execute("INSERT INTO maskinfo (take_mask, no_mask, time, status) values (?,?, ?);", z)
        self.mask_num = 0
        self.no_mask_num = 0

    def ShowVideo(self, cap, label, ai_switch=True):
        """
        显示视频
        :param cap: 打开视频的控件
        :param label: 标签控件
        :param ai_switch: 是否启动AI标识符
        :return:
        """
        self.is_start = True
        self.is_save = False
        width = 400
        height = 300
        self.lock.acquire()
        flag = 0
        while not self.is_exit:
            flag, frame = cap.read()
            if flag == 5:
                if self.LabelSetPic(label, frame, width, height, ai_switch, True):
                    break
            elif self.LabelSetPic(label, frame, width, height, ai_switch, False):
                break
        self.lock.release()
        # 计数器清零
        self.mask_num = 0
        self.no_mask_num = 0
        cap.release()
        if ai_switch:
            label.clear()
