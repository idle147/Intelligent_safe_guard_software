from PyQt5.QtGui import QPalette, QBrush, QPixmap, QIcon
from PyQt5.QtWidgets import QMessageBox
import Global
import numpy as np


class CWinOpt():
    def __init__(self):
        self.mesBox = QMessageBox()
        # 设置窗体ICON
        self.mesBox.setWindowIcon(QIcon("ui_file/resource/icon/icon.png"))
        # 样式设置
        self.mesBox.setStyleSheet(Global.QSS)

    # 绘制背景图片
    # "./ui_file/resource/img/background5.jpg"
    @staticmethod
    def drawn(picture_name, win):
        win.palette = QPalette()
        win.palette.setBrush(QPalette.Background, QBrush(QPixmap(picture_name)))
        win.setPalette(win.palette)

    @staticmethod
    def QPixmapToMat(qtpixmap):
        qimg = qtpixmap.toImage()
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        return result

    def OneBtnMsgBox(self, title, content, type):
        self.mesBox.setWindowTitle(title)
        self.mesBox.setText(content)
        self.mesBox.setIcon(type)
        # 按钮设置
        self.mesBox.setStandardButtons(QMessageBox.Yes)
        self.mesBox.button(QMessageBox.Yes).setText('确认')
        # 执行
        self.mesBox.exec_()

    def TwoBtnMsgBox(self, title, content, type):
        self.mesBox.setWindowTitle(title)
        self.mesBox.setText(content)

        # 设置窗体ICON
        self.mesBox.setWindowIcon(QIcon("ui_file/resource/icon/icon.png"))
        self.mesBox.setIcon(type)

        # 按钮设置
        self.mesBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_yes = self.mesBox.button(QMessageBox.Yes)
        btn_yes.setText('赶紧确定')
        btn_no = self.mesBox.button(QMessageBox.No)
        btn_no.setText('容我三思')
        # 执行
        self.mesBox.exec_()

        if self.mesBox.clickedButton() == btn_yes:
            return True
        elif self.mesBox.clickedButton() == btn_no:
            return False
