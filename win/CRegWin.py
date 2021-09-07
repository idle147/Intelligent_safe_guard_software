import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from CAiFaceDetection import CAiFaceDetection
from CCamOpt import CCamOpt
from CNetWork import CNetWork
from Global import BACKGROUND_PATH, CORRECT_PIC, ERROR_PIC, face_detection
from ui_file.ui_reg import *
from win.CWinOpt import *


class CRegWin(QWidget, Ui_reg):
    _startPos = None
    _endPos = None
    _isTracking = False

    # 获取相机
    def __init__(self, mask_check, parent=None):
        super(CRegWin, self).__init__()  # super() 函数是用于调用父类(超类)的一个方法。
        self.setupUi(self)
        self.__parent = parent
        self.__isFace = False
        self.__res = False
        self.__output_res = []
        self.__status = 0

        # 实例化相关类
        self.win_opt = CWinOpt()
        self.ai_face = CAiFaceDetection()
        self.mask_check = mask_check
        self.__c_timer = QTimer()
        self.network = CNetWork()

        # 界面设置
        self.win_opt.drawn(BACKGROUND_PATH, self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.edit_user_name.clear()
        self.edit_user_name.setTextMargins(15, 0, 0, 0)

        # 连接槽函数
        self.__c_timer.timeout.connect(self.showTime)  # 这个通过调用槽函数来刷新时间
        #self.__c_timer.timeout.connect(self.BtnConnectInfo)  # 这个通过调用槽函数来刷新时间

        self.btn_get_face.clicked.connect(self.SlotGetFace)  # 捕获人脸按钮
        self.btn_reget.clicked.connect(self.SlotReGet)  # 捕获人脸按钮
        self.btn_return.clicked.connect(self.SlotReturn)  # 跳转到上级菜单
        self.btn_decide.clicked.connect(self.SlotDecide)  # 确定发送图片信息

        # 启动定时器
        self.startTimer()

        # 启动注册
        self.StartCam()

    # 启动相机
    def StartCam(self):
        # 设置标签
        self.Cam_Opt = CCamOpt("./temp/", 0, self.win_opt, self.ai_face, self.mask_check)
        self.Cam_Opt.ThreadOptShowVideo('', self.label_cam, False, False)

    # 判断是否连接成功
    def BtnConnectInfo(self):
        status = self.network.ConnectCheck()
        if status == 0:
            self.pushButton.setIcon(QIcon(CORRECT_PIC))
            self.pushButton.setText("百度AI连接成功")
        else:
            self.pushButton.setIcon(QIcon(ERROR_PIC))
            info = "连接失败,错误码:" + str(status)
            self.pushButton.setText(info)

    # 改变鼠标事件
    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    # 进行时间
    def showTime(self):
        time = QDateTime.currentDateTime()  # 获取当前时间
        time_display = time.toString("yyyy-MM-dd hh:mm:ss")  # 格式化一下时间
        self.edit_time.setText(time_display)

    def startTimer(self):
        self.__c_timer.start(1000)  # 每隔一秒刷新一次，这里设置为1000ms
        self.showTime()

    def SlotGetFace(self):
        str = self.edit_user_name.text()
        if len(str) == 0:
            self.win_opt.OneBtnMsgBox("警告", "请先输入用户名", QMessageBox.Warning)
            return
        else:
            self.Cam_Opt.SavePic()
            time.sleep(0.1)
            if self.Cam_Opt.ReadSaveRes():
                self.win_opt.OneBtnMsgBox("提示", "照片捕获成功", QMessageBox.Information)
                # 检查照片内是否有人脸
                self.FaceJudge()
            else:
                self.win_opt.OneBtnMsgBox("提示", "照片捕获失败", QMessageBox.Critical)

    def SlotReGet(self):
        # 已经启动了
        if self.Cam_Opt.is_start:
            self.win_opt.OneBtnMsgBox("提示", "相机镜头已经魔法展开了!", QMessageBox.Critical)
        else:
            self.Cam_Opt.ThreadOptShowVideo('', self.label_cam, False, False)

    def SlotReturn(self):
        # 关闭本窗口,打开父窗口
        if self.__parent != None:
            self.__parent.show()
        self.close()

    def SlotDecide(self):
        # 判断是否有可发送的数据
        if len(self.__output_res) == 0:
            self.win_opt.OneBtnMsgBox("警告", "未捕获照片or捕获照片非法", QMessageBox.Critical)
            return
        # 去百度网盘检测是否有重复脸
        res = self.ai_face.UserQuire(self.edit_user_name.text(), "safeGuard")
        if res == '0':
            self.win_opt.OneBtnMsgBox("警告", "存在同名用户,请重试!!", QMessageBox.Critical)
            return
        # 判断是否有重复的人脸
        res = self.ai_face.FaceResearch(self.__output_res[0], "safeGuard")
        if len(res) == 0:
            # 写入百度云人脸库
            res = self.ai_face.FaceAdd(self.edit_user_name.text(), self.__output_res[0], "safeGuard")
            if res:
                self.win_opt.OneBtnMsgBox("提示", "人脸注册成功!", QMessageBox.Information)
            else:
                self.win_opt.OneBtnMsgBox("提示", "人脸注册失败, 请检查百度API连接!", QMessageBox.Information)
        else:
            self.win_opt.OneBtnMsgBox("警告", "系统已经存在该人脸, 请直接用该脸登陆, 谢谢", QMessageBox.Critical)

    def FaceJudge(self):
        img = self.label_cam.pixmap()
        img = face_detection.QpixmapToCvImg(img)
        self.__output_res = face_detection.FaceDetection(img)
        if len(self.__output_res) == 0:
            self.win_opt.OneBtnMsgBox("提示", "未识别到人脸,请重试!", QMessageBox.Critical)
            self.SlotReGet()
        elif len(self.__output_res) == 1:
            self.win_opt.OneBtnMsgBox("提示", "成功捕获人脸!", QMessageBox.Information)
        else:
            self.win_opt.OneBtnMsgBox("提示", "识别到多张人脸,请重试!", QMessageBox.Critical)
            self.SlotReGet()
