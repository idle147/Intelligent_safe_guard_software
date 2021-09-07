import time

from ui_file.ui_login import *
from win.CRegWin import CRegWin
from win.CMainWin import *
from CNetWork import *


class CLoginWin(QWidget, Ui_login):
    """登陆窗口"""
    _startPos = None
    _endPos = None
    _isTracking = False

    def __init__(self, mask_check, parent=None):
        """
        登陆窗口初始化
        :param mask_check: mask识别类函数
        :param parent: 父窗口
        """
        super(CLoginWin, self).__init__()  # super() 函数是用于调用父类(超类)的一个方法。
        self.setupUi(self)
        self.__parent = parent
        self.output_res = []

        # 实例化相关类
        self.win_opt = CWinOpt()
        self.ai_face = CAiFaceDetection()
        self.mask_check = mask_check
        self.Cam_Opt = CCamOpt("./temp/", 0, self.win_opt, self.ai_face, self.mask_check)
        self.network = CNetWork()
        # 界面设置
        self.win_opt.drawn(BACKGROUND_PATH, self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框

        # 槽函数相关连接
        self.btn_get_face.clicked.connect(self.SlotGetFace)  # 捕获人脸按钮
        self.btn_reget.clicked.connect(self.SlotReGet)  # 重新捕获按钮
        self.btn_reg.clicked.connect(self.SlotToReg)  # 跳转到注册界面
        self.btn_return.clicked.connect(self.SlotReturn)  # 跳转到上级菜单
        self.btn_decide.clicked.connect(self.SlotDecide)  # 确定发送图片信息

        # 判断连接的定时器
        self.timer = QTimer()
        self.timer.start(2 * 1000)
        #self.timer.timeout.connect(self.BtnConnectInfo)

        # 启动摄像头
        # ThreadOptShowVideo(self, file_name, label, ai_switch=True, class_mode=False):
        self.Cam_Opt.ThreadOptShowVideo('', self.label_cam, False, False)

        # # 发起连接
        # self.StartConnect()

    # 点击确定连接
    def SlotDecide(self):
        """
        点击确定按钮
        :return:
        """
        # 调用百度AI接口, 进行人脸判断
        if len(self.output_res) == 0:
            self.win_opt.OneBtnMsgBox("提示", "您未捕获人脸", QMessageBox.Information)
        else:
            res = self.ai_face.FaceLogin(self.output_res[0], "safeGuard")
            if len(res) == 0:
                self.win_opt.OneBtnMsgBox("警告", "人脸登录识别失败", QMessageBox.Critical)
            else:
                self.win_opt.OneBtnMsgBox("提示", "登录成功!", QMessageBox.Information)
                # 关闭摄像头
                self.Cam_Opt.SavePic()
                # 跳转到主界面界面
                main_win = CMainWin(self.Cam_Opt, res, self.label_cam.pixmap(), self)
                main_win.show()
                # 关闭登陆界面
                self.close()
        return

    # 判断是否连接成功
    def BtnConnectInfo(self):
        """
        定时器判断是否成功连接
        :return:
        """
        status = self.network.ConnectCheck()
        if status == 0:
            self.btn_connect.setIcon(QIcon(CORRECT_PIC))
            self.btn_connect.setText("百度AI连接成功")
        else:
            self.btn_connect.setIcon(QIcon(ERROR_PIC))
            info = "连接失败,错误码:" + str(status)
            self.btn_connect.setText(info)

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

    # 相关槽函数
    def SlotGetFace(self):
        """
        槽函数: 获取人脸
        :return:
        """
        self.Cam_Opt.SavePic()
        time.sleep(0.1)  # 休眠一毫秒
        print(self.Cam_Opt.ReadSaveRes())
        if self.Cam_Opt.ReadSaveRes():
            self.win_opt.OneBtnMsgBox("提示", "图片抓取成功", QMessageBox.Information)
            # 检查照片内是否有人脸
            self.FaceJudge()
        else:
            self.win_opt.OneBtnMsgBox("提示", "图片抓取失败", QMessageBox.Critical)

    def SlotReGet(self):
        """
        槽函数, 重新捕获
        :return:
        """
        # 已经启动了
        if self.Cam_Opt.is_start:
            self.win_opt.OneBtnMsgBox("提示", "相机镜头已经魔法展开了!", QMessageBox.Critical)
        else:
            self.Cam_Opt.SavePic()
            self.Cam_Opt.ThreadOptShowVideo('', self.label_cam, False, False)

    def SlotToReg(self):
        """
        槽函数, 跳转到登陆界面
        :return:
        """
        # 确认跳转
        res = self.win_opt.TwoBtnMsgBox("重复", "是否确认跳转到注册界面?", QMessageBox.Critical)
        if res == True:
            # 进入注册界面
            if self.__parent != None:
                self.Cam_Opt.ExitCam()
                # 跳转到注册界面
                time.sleep(0.1)
                self.__parent.SlotToRegWin()
                # 关闭本窗口
                self.close()
            else:
                self.win_opt.OneBtnMsgBox("提示", "无法进入注册界面,请从主界面进入!", QMessageBox.Critical)

    def SlotReturn(self):
        """
        槽函数: 返回上级菜单
        :return:
        """
        # 关闭本窗口,返回主界面
        if self.__parent != None:
            self.__parent.show()
        self.close()

    def FaceJudge(self):
        """
        槽函数: 人脸判断
        :return:
        """
        img = self.label_cam.pixmap()
        img = face_detection.QpixmapToCvImg(img)
        self.output_res = face_detection.FaceDetection(img)
        if len(self.output_res) == 0:
            self.win_opt.OneBtnMsgBox("提示", "未捕获到人脸,请重试!", QMessageBox.Critical)
            self.SlotReGet()
        elif len(self.output_res) == 1:
            self.win_opt.OneBtnMsgBox("提示", "成功捕获人脸!", QMessageBox.Information)
        else:
            self.win_opt.OneBtnMsgBox("提示", "捕获到多张人脸,请重试!", QMessageBox.Critical)
            self.SlotReGet()
