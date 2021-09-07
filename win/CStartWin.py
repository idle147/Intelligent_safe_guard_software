from CMaskDetection import CMaskDetection
from ui_file.ui_start import *
from win.CLoginWin import *
from win.CRegWin import *
from PyQt5.QtWidgets import QMessageBox, QMainWindow
import sys


class CStartWin(QMainWindow, Ui_start):
    """
    主界面
    """

    def __init__(self):
        super(QMainWindow, self).__init__()  # super() 函数是用于调用父类(超类)的一个方法。
        self.setupUi(self)
        # 连接槽函数
        self.btn_face_reg.clicked.connect(self.SlotToRegWin)
        self.btn_face_recognition.clicked.connect(self.SlotToRecognition)
        self.btn_exit.clicked.connect(self.SlotToExit)
        # 创建对象
        self.mask_check = CMaskDetection()
        self.win_opt = CWinOpt()

    def SlotToRegWin(self):
        """
        跳转到注册界面
        :return:
        """
        self.reg_win = CRegWin(self.mask_check, self)
        self.reg_win.show()
        self.hide()

    def SlotToRecognition(self):
        """
        跳转到人脸识别界面
        :return:
        """
        self.login_win = CLoginWin(self.mask_check, self)
        self.login_win.show()
        self.hide()

    def SlotToExit(self):
        """
        退出程序
        :return:
        """
        if self.win_opt.TwoBtnMsgBox('警告', '是否退出程序?', QMessageBox.Warning):
            sys.exit(0)
