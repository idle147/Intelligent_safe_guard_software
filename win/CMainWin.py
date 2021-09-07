import os
import shutil
import time
from datetime import datetime
import pandas as pd

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from CAiFaceDetection import *
from CCamOpt import CCamOpt
from CMySqlOpt import *
from CNetWork import *
from CSqliteOpt import CSqliteOpt
from Global import *
from SystemSet import *
from ui_file.ui_main import *
from win.CWinOpt import *


def ListSplit(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


class CMainWin(QWidget, Ui_main):
    """
        主要功能界面
    """
    _startPos = None
    _endPos = None
    _isTracking = False

    def __init__(self, cam, user_info, img, parent=None):
        """
        界面初始化
        :param cam: 相机镜头
        :param user_info: 用户信息
        :param img:  图像
        :param parent: 父窗口
        """
        super(CMainWin, self).__init__()  # super() 函数是用于调用父类(超类)的一个方法。
        self.setupUi(self)
        self.__parent = parent
        self.__output_res = []
        self.Cam_Opt = cam

        # 设置名字
        self.label_user_name.setText(user_info)
        # 设置头像
        # height, width, channel = img.shape
        # bytesPerLine = 3 * width
        # qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        img = img.scaled(self.label_user_pic.width() - 1, self.label_user_pic.height() + 2)
        self.label_user_pic.setPixmap(img)

        # 在每个人脸框下绘制按钮
        self.btn_dict = {}
        self.click_Num = {}
        self.face_pic = []
        self.face_local = []

        # 相关类实例化
        self.__c_win_opt = CWinOpt()
        self.__c_db_opt = CDbOpt()
        self.__c_sqlite_opt = CSqliteOpt()
        self.__c_face_detect = CFaceDetection()
        self.__c_ai_face = CAiFaceDetection()

        # 边框设置
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.edit_std_id.setValidator(QtGui.QIntValidator())  # 设置只能输入int类型的数据
        self.btn_screenshoot_yes.hide()
        self.btn_screenshoot_no.hide()

        # 表格视窗设置
        self.tb_error.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格禁止编辑
        self.tb_stu.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格禁止编辑
        self.tb_error_2.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格禁止编辑
        self.tb_error.setSelectionMode(0)  # 设置不可选中
        self.tb_error_2.setSelectionMode(0)  # 设置不可选中
        self.tb_stu.setSelectionMode(0)  # 设置不可选中
        self.tb_stu.horizontalHeader().setSectionResizeMode(1)  # 使列表自适应宽度

        # tab_7 设置
        self.SlotNumSet()
        self.is_delete = 1
        self.label_12.setText("校园防御系统V1.0")

        # 页码的设置
        self.page_all = 0
        self.tab5_displayRes = []
        self.label_dict = {}
        self.current_page_2.clear()

        # 当前时间设置
        self.de_start.setDateTime(QDateTime.currentDateTime())
        self.de_start.setMaximumDateTime(QDateTime.currentDateTime())
        self.de_end.setDateTime(QDateTime.currentDateTime())
        self.de_end.setMaximumDateTime(QDateTime.currentDateTime())
        self.de_start_3.setDateTime(QDateTime.currentDateTime())
        self.de_start_3.setMaximumDateTime(QDateTime.currentDateTime())
        self.de_end_3.setDateTime(QDateTime.currentDateTime())
        self.de_end_3.setMaximumDateTime(QDateTime.currentDateTime())

        # 槽函数设置
        self.tabWidgetMenuBar.currentChanged.connect(self.SlotPageChange)
        self.btn_exit.clicked.connect(self.SlotExit)
        self.btn_minimum.clicked.connect(self.SlotMiniWin)
        self.btn_close.clicked.connect(self.SlotClose)

        # tab_1 设置
        self.btn_open_file.clicked.connect(self.SlotOpenFile)
        self.btn_open_cam.clicked.connect(self.SlotOpenCam)
        self.btn_decide.clicked.connect(self.SlotDecide)
        self.btn_open_file_2.clicked.connect(
            lambda: self.SlotOpenVideoFile(self.label_pic_2, ai_switch=True, class_mode=False))
        self.btn_open_cam_2.clicked.connect(
            lambda: self.SlotOpenCamCheck(self.label_pic_2, ai_switch=True, class_mode=False))
        self.btn_open_file_3.clicked.connect(
            lambda: self.SlotOpenVideoFile(self.label_pic_3, ai_switch=False, class_mode=True))
        self.btn_open_cam_3.clicked.connect(
            lambda: self.SlotOpenCamCheck(self.label_pic_3, ai_switch=False, class_mode=True))

        # tab2--学院信息管理
        self.btn_up_page.clicked.connect(lambda: self.SlotChangePage(self.current_page_1, None, False))
        self.btn_down_page.clicked.connect(lambda: self.SlotChangePage(self.current_page_1, None, True))

        # tab3--教室监控模式
        self.btn_screenshoot.clicked.connect(self.SlotScreenShot)
        self.btn_screenshoot_no.clicked.connect(self.SlotCancelSubmit)
        self.btn_screenshoot_yes.clicked.connect(self.SlotSubmit)

        # tab5-错误数据查看
        self.btn_query.clicked.connect(lambda: self.SlotQuery(self.current_page_2, self.tb_error))
        self.btn_up_page_2.clicked.connect(lambda: self.SlotChangePage(self.current_page_2, self.tb_error, False))
        self.btn_down_page_2.clicked.connect(lambda: self.SlotChangePage(self.current_page_2, self.tb_error, True))

        # tab6-检测数据导出
        self.btn_query_2.clicked.connect(self.SlotCheckQuery)
        self.btn_query_3.clicked.connect(self.SlotExport)

        # tab7--系统设置
        self.btn_default.clicked.connect(self.SlotDefaultSet)
        self.indicator.clicked.connect(self.SlotChangeDeleteState)
        self.btn_decide_set.clicked.connect(self.SlotSetDecideSubMit)
        self.btn_model_input.clicked.connect(self.SlotModelInput)

    def SlotExport(self):
        """
        槽函数: 导出信息
        :return:
        """
        if self.__c_win_opt.TwoBtnMsgBox("信息", "是否确认导出,请检查表格是否有,否则将导出空数据", QMessageBox.Information):
            dir = QFileDialog.getExistingDirectory(self, "选择导出目录", os.getcwd())
            if dir == "":
                return
            path = dir + '/' + str(time.time()) + '.csv'
            list = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for x in range(1, self.tb_error_2.rowCount()):
                for y in range(0, self.tb_error_2.columnCount()):
                    item = self.tb_error_2.item(x, y)
                    if not item:
                        continue
                    list[x - 1][y] = item.text()
            # 创建CSV文件
            test = pd.DataFrame(data=list)
            test.to_csv(path, encoding="utf_8_sig")
            self.__c_win_opt.OneBtnMsgBox("信息", "导出完毕,导出路径:" + path, QMessageBox.Information)

    def SlotCheckQuery(self):
        """
        槽函数: 检查查询
        :return:
        """
        title = self.de_start_3.text() + ' 至 ' + self.de_end_3.text()
        self.tb_error_2.setSpan(0, 0, 1, 3)
        self.tb_error_2.setItem(0, 0, QTableWidgetItem(title))
        self.tb_error_2.item(0, 0).setTextAlignment(Qt.AlignCenter)
        num = [[0, 0], [0, 0], [0, 0]]

        for i in (1, 2, 3):
            sql1 = "SELECT SUM(take_mask), SUM(no_mask) FROM maskinfo WHERE time >= ? and  time <= ? and status = ?;"
            res = self.__c_sqlite_opt.query(sql1, (self.de_start_3.text(), self.de_end_3.text() + ' 23:59:59', i))
            if res[0][0] == None and res[0][1] != None:
                num[i - 1][0] = '0'
                num[i - 1][1] = str(res[0][1])
            elif res[0][0] != None and res[0][1] == None:
                num[i - 1][0] = str(res[0][0])
                num[i - 1][1] = '0'
            elif res[0][0] != None and res[0][1] != None:
                num[i - 1][0] = str(res[0][0])
                num[i - 1][1] = str(res[0][1])
            else:
                num[i - 1][0] = '0'
                num[i - 1][1] = '0'

        for i in range(2, 5):
            self.tb_error_2.setItem(i, 1, QTableWidgetItem(num[i - 2][0]))
            self.tb_error_2.setItem(i, 2, QTableWidgetItem(num[i - 2][1]))
            self.tb_error_2.item(i, 1).setTextAlignment(Qt.AlignCenter)
            self.tb_error_2.item(i, 2).setTextAlignment(Qt.AlignCenter)

        self.__c_win_opt.OneBtnMsgBox("信息", "查询完毕", QMessageBox.Information)

    def SlotPageChange(self):
        """
        槽函数: 当页面进行切换时, 触发的槽函数
        :return:
        """
        if self.tabWidgetMenuBar.currentIndex() == 1:
            self.current_page_1.setText('1')
            self.tab2_displayRes = []
            self.StuShowTable(1)

    # 是否确认退出
    def SlotExit(self):
        """
        槽函数: 是否确认退出
        :return:
        """
        if self.__c_win_opt.TwoBtnMsgBox("注意", "是否确认退出", QMessageBox.Information):
            exit(0)

    # tab2 显示页面
    def StuShowTable(self, current_page):
        """
        显示tab2的页面
        :param current_page: 当前页, 进行切换
        :return: 返回当前结果
        """
        self.tb_stu.clear()
        self.tab2_displayRes = []
        limit_num = str((current_page - 1) * self.tb_stu.rowCount())
        page_size = str(self.tb_stu.rowCount())
        sql = "select stu_id, stu_name from stu_table WHERE stu_status = 'normal' order by stu_id asc limit "
        sql += limit_num + ',' + page_size + ';'
        # 查询mysql的stu表
        # 传输数据, 判断该学号下有无人脸, 是否需要进行更新
        self.tab2_displayRes = self.__c_db_opt.Db_SELECT_SQL(sql)
        if len(self.tab2_displayRes) == 0:
            return False
        # 为每一行添加item
        for i in range(len(self.tab2_displayRes)):
            path = CONFIG["@client_config"]["stu_face"] + str(self.tab2_displayRes[i][0]) + '.jpg'
            # 往第1, 2列添加数据
            item1 = QTableWidgetItem(str(self.tab2_displayRes[i][0]))
            item2 = QTableWidgetItem(self.tab2_displayRes[i][1])
            self.tb_stu.setItem(i, 0, item1)
            self.tb_stu.item(i, 0).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tb_stu.setItem(i, 1, item2)
            self.tb_stu.item(i, 1).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # 往第3列添加标签控件
            self.tb_stu.setCellWidget(i, self.tb_stu.rowCount() - 2, self.labelForRow(path))
            # 往第4列添加修改or删除控件
            self.tb_stu.setCellWidget(i, self.tb_stu.rowCount() - 1, self.buttonForRow())
        return True

    # tab2 相关操作
    def labelForRow(self, path):
        """
        跳动图像库, 进行图片展示
        :param path: 路径
        :return:
        """
        label = QLabel()
        label.setPixmap(QPixmap(path))
        label.setScaledContents(True)  # 让图片自适应label大小
        # 设置布局
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent")
        hLayout = QHBoxLayout()
        hLayout.addWidget(label)
        hLayout.setAlignment(widget, Qt.AlignCenter)  # 设置水平居中
        hLayout.setContentsMargins(15, 5, 10, 5)  # 设置部件周围的左、上、右、下边距
        widget.setLayout(hLayout)  # 添加布局
        return widget

    def buttonForRow(self):
        """
        为每一行添加按钮
        :return:
        """
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent")
        # 修改
        updateBtn = QPushButton('修改')
        updateBtn.setStyleSheet(''' text-align : center;
                                              background-color : NavajoWhite;
                                              height : 30px;
                                              weight : 70px;
                                              border-style: outset;
                                              font : 13px  ''')

        # 删除
        deleteBtn = QPushButton('删除')
        deleteBtn.setStyleSheet(''' text-align : center;
                                        background-color : LightCoral;
                                        height : 30px;
                                        weight : 70px;
                                        border-style: outset;
                                        font : 13px; ''')
        # 槽函数连接
        updateBtn.clicked.connect(self.UpdateButton)
        deleteBtn.clicked.connect(self.DeleteButton)
        # 布局操作
        hLayout = QHBoxLayout()
        hLayout.addWidget(updateBtn)
        hLayout.addWidget(deleteBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def UpdateButton(self):
        """
        更新按钮
        :return:
        """
        if self.__c_win_opt.TwoBtnMsgBox("注意", "请确认是否要修改该条目", QMessageBox.Information):
            button = self.sender()
            if button:
                # 确定位置的时候这里是关键
                row = self.tb_stu.indexAt(button.parent().pos()).row()
                # 根据行数确定ID
                stu_id = str(self.tb_stu.item(row, 0).text())
                stu_name = self.tb_stu.item(row, 1).text()
                # 设置相应的信息
                self.edit_std_id.setText(stu_id)
                self.edit_std_name.setText(stu_name)
                # 跳转到tab_1
                self.tabWidgetMenuBar.setCurrentIndex(0)

    def DeleteButton(self):
        """
        删除按钮
        :return:
        """
        if self.__c_win_opt.TwoBtnMsgBox("注意", "请确认是否要删除该跳条目", QMessageBox.Information):
            button = self.sender()
            if button:
                # 确定位置的时候这里是关键
                row = self.tb_stu.indexAt(button.parent().pos()).row()
                # 根据行数确定ID
                stu_id_delete = str(self.tb_stu.item(row, 0).text())
                # 删除百度AI
                # 百度AI进行回滚操作
                face_token = self.__c_ai_face.GetFaceToken(stu_id_delete)
                if not self.__c_ai_face.FaceDelete(stu_id_delete, face_token):
                    self.__c_win_opt.OneBtnMsgBox("警告", "百度AI数据删除失败", QMessageBox.Warning)
                    return
                # 根据ID将状态标识设置为删除状态
                sql = "UPDATE stu_table SET stu_status = 'delete' WHERE stu_id="
                sql += stu_id_delete + ';'
                if self.__c_db_opt.Db_Update_SQL(sql):
                    self.__c_win_opt.OneBtnMsgBox("注意", "删除成功", QMessageBox.Information)
                    self.StuShowTable(int(self.current_page_1.text()))
                else:
                    self.__c_win_opt.OneBtnMsgBox("注意", "删除失败", QMessageBox.Warning)

    # 模型导入
    def SlotModelInput(self):
        """
        模型导入
        :return:
        """
        if not self.__c_win_opt.TwoBtnMsgBox("注意", "是否确认导入新模型(将会覆盖旧模型)?", QMessageBox.Information):
            return
        model_name, model_type = QFileDialog.getOpenFileName(self, "选择模型文件", "/", "模型文件(*.model);;")
        if model_name == "" or model_type != "model_type":
            self.__c_win_opt.OneBtnMsgBox("警告", "未选择或选择文件不复合规范", QMessageBox.Warning)
        else:
            try:
                shutil.copy(model_name, CONFIG["@mask_detection"]["model_name"] + ".data-00000-of-00001")
            except:
                self.__c_win_opt.OneBtnMsgBox("注意", "模型导入出现错误, 请检查是否是同一文件", QMessageBox.Information)
            else:
                self.__c_win_opt.OneBtnMsgBox("注意", "模型导入成功", QMessageBox.Information)

    # 确认提交
    def SlotSetDecideSubMit(self):
        """
        修改的配置, 确认提交
        :return:
        """
        if not self.__c_win_opt.TwoBtnMsgBox("注意", "是否确认修改配置?", QMessageBox.Information):
            return
        if self.NullValueJudge():
            CONFIG["@client_config"]["soft_version"] = self.label_12.text()[-2:0]
            CONFIG["@client_config"]["server_ip_add"] = self.edit_serve_id.text()
            CONFIG["@client_config"]["server_ip_port"] = int(self.edit_serve_port.text())
            CONFIG["@client_config"]["model_save_addr"] = "model/"
            CONFIG["@client_config"]["system_storage_size"] = int(self.edit_large.text())
            CONFIG["@client_config"]["is_delete"] = self.is_delete
            CONFIG["@client_config"]["error_image_path"] = "error_image/"
            CONFIG["@client_config"]["stu_face"] = "stu_face/"

            CONFIG["@baidu_api"]["APP_ID"] = self.edit_app_id.text()
            CONFIG["@baidu_api"]["API_KEY"] = self.edit_api_key.text()
            CONFIG["@baidu_api"]["SECRET_KEY"] = self.edit_secret_key.text()

            CONFIG["@mysql_opt"]["mysql_db"] = "recordDB"
            CONFIG["@mysql_opt"]["mysql_host"] = self.edit_db_ip.text()
            CONFIG["@mysql_opt"]["mysql_port"] = int(self.edit_db_port.text())
            CONFIG["@mysql_opt"]["mysql_user"] = self.edit_db_user.text()
            CONFIG["@mysql_opt"]["mysql_pwd"] = self.edit_db_key.text()
            CONFIG["@mysql_opt"]["mysql_charset"] = "utf8"

            CONFIG["@mask_detection"]["model_name"] = "model/train.model"
            CONFIG["@mask_detection"]["IMAGE_SIZE"] = 150
            CONFIG["@mask_detection"]["LEARNING_RATE"] = 0.0001

            CONFIG["@Sqlite3"]["db_file"] = "dataBase/error_face.db"

            # 编写成字典的形式
            info = json.dumps(CONFIG, indent=4)
            # 写入配置文件
            fo = open("config/config.json", "w")
            fo.write(info)
            fo.close()
            # 弹出提示
            self.__c_win_opt.OneBtnMsgBox("注意", "配置修改成功", QMessageBox.Information)

    # 空值判断
    def NullValueJudge(self):
        """
        判断是否有空值
        :return:
        """
        if self.edit_app_id.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "百度APP_ID不能为空", QMessageBox.Information)
            return False
        if self.edit_api_key.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "百度API_KEY不能为空", QMessageBox.Information)
            return False
        if self.edit_secret_key.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "百度SECRET_KEY不能为空", QMessageBox.Information)
            return False
        if self.edit_db_ip.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "数据库I地址不能为空", QMessageBox.Information)
            return False
        if self.edit_db_port.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "数据库端口地址不能为空", QMessageBox.Information)
            return False
        if self.edit_db_user.text() == "" or self.edit_db_key.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "数据库用户名/密码不能为空", QMessageBox.Information)
            return False
        if self.edit_serve_id.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "服务器Ip地址不能为空", QMessageBox.Information)
            return False
        if self.edit_serve_port.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "数据库端口地址不能为空", QMessageBox.Information)
            return False
        if self.edit_large == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "系统存储大小不为空", QMessageBox.Information)
            return False
        return True

    # 可否删除
    def SlotChangeDeleteState(self):
        """
        是否可以删除数据
        :return:
        """
        if self.is_delete == 1:
            self.is_delete = 0
        else:
            self.is_delete = 1
        if self.is_delete:
            self.indicator.setText("可 以 删 除")
        else:
            self.indicator.setText("不 可 以 删 除")

    # 恢复默认值
    def SlotDefaultSet(self):
        """
        回复默认值操作
        :return:
        """
        # 是否恢复默认值
        if self.__c_win_opt.TwoBtnMsgBox("注意", "是否确定恢复默认值", QMessageBox.Information):
            self.edit_app_id.setText("23885551")
            self.edit_api_key.setText("m3OnUadV0w79rZkomQZtsrNV")
            self.edit_secret_key.setText("pCTlAp6AjGqkGCyh9u8TVcbxR5bbswrG")
            self.edit_db_ip.setText("47.98.60.15")
            self.edit_db_port.setText("3306")
            self.edit_db_user.setText("root")
            self.edit_db_key.setText("000000")
            self.edit_serve_id.setText("192.168.1.1")
            self.edit_serve_port.setText("8080")
            self.indicator.setText("可 以 删 除")
            self.is_delete = 1
            self.edit_large.setText("8080")

    # 数值设置
    def SlotNumSet(self):
        """
        相关界面设置
        :return:
        """
        self.label_12.setText("校园防御系统V" + GetClientConf("soft_version"))

        self.edit_app_id.setText(GetBaiDuConf("APP_ID"))
        self.edit_api_key.setText(GetBaiDuConf("API_KEY"))
        self.edit_secret_key.setText(GetBaiDuConf("SECRET_KEY"))

        self.edit_db_ip.setText(GetMysqlConf("mysql_host"))
        self.edit_db_port.setText(str(GetMysqlConf("mysql_port")))
        self.edit_db_user.setText(GetMysqlConf("mysql_user"))
        self.edit_db_key.setText(GetMysqlConf("mysql_pwd"))

        self.edit_serve_id.setText(GetClientConf("server_ip_add"))
        self.edit_serve_port.setText(str(GetClientConf("server_ip_port")))

        if GetClientConf("is_delete"):
            self.indicator.setText("可 以 删 除")
        else:
            self.indicator.setText("不 可 以 删 除")

        self.edit_large.setText(str(GetClientConf("system_storage_size")))

    # 切换页码
    def SlotChangePage(self, current_page_con, table_widget, is_down=True):
        """
        切换页码
        :param current_page_con: 当前页控件
        :param table_widget: 桌面控件
        :param is_down: 是否是向下
        :return:
        """
        if current_page_con.text() == "":
            self.__c_win_opt.OneBtnMsgBox("注意", "您未点击查询", QMessageBox.Information)
            return

        # 判断是增还是减
        current_page = int(current_page_con.text())
        if is_down:  # 增加
            current_page += 1
        else:  # 减少
            current_page -= 1

        # 判断是否超过范围
        if current_page < 1:
            self.__c_win_opt.OneBtnMsgBox("注意", "没有上一页", QMessageBox.Information)
            return

        # 判断页码
        if table_widget == None:
            # 查询下一页的东西看看能不能查到
            if self.StuShowTable(current_page) == False:
                self.__c_win_opt.OneBtnMsgBox("注意", "没有下一页", QMessageBox.Information)
                self.StuShowTable(int(current_page_con.text()))
                return

        # 进行页面切换的操作
        current_page_con.setText(str(current_page))
        if table_widget != None:
            # 展示信息
            self.PageQuery(current_page, table_widget)

    # 查询提交
    def SlotQuery(self, current_page_con, tableWidget):
        """
        查询结果提交
        :param current_page_con:  当前页控件
        :param tableWidget: tb控件
        :return:
        """
        # 执行时间范围内的查询
        sql = "SELECT error_time FROM error_record_table WHERE error_time >= ? and  error_time <= ?;"
        res = self.__c_sqlite_opt.query(sql, (self.de_start.text(), self.de_end.text() + ' 23:59:59'))
        # 清除表格
        tableWidget.clear()
        current_page_con.clear()
        self.tab5_displayRes = []
        # 每页展示的数量
        page_every = tableWidget.columnCount() * tableWidget.rowCount()
        if len(res) > page_every:
            self.__c_win_opt.OneBtnMsgBox("注意", "数据查询完毕, 需要分页", QMessageBox.Information)
            # 对数组结果进行分割
            self.tab5_displayRes = ListSplit(res, page_every)
            # 设置当前页
            current_page_con.setText('1')
            # 展示第一页
            self.PageQuery(1, tableWidget)
        elif page_every >= len(res) > 0:
            self.__c_win_opt.OneBtnMsgBox("注意", "数据查询完毕, 无需分页", QMessageBox.Information)
            # 对数组结果进行分割
            self.tab5_displayRes = ListSplit(res, len(res))
            # 设置当前页
            current_page_con.setText('1')
            # 展示第一页
            self.PageQuery(1, tableWidget)
        else:
            self.__c_win_opt.OneBtnMsgBox("注意", "查无数据", QMessageBox.Information)

    # 页面查询
    def PageQuery(self, current_page, tableWidget):
        """
        页面查询
        :param current_page: 当前页
        :param tableWidget: tb控件
        :return:
        """
        # 清除旧数据
        tableWidget.clear()
        self.current_page_2.setText(str(current_page))
        current_page = current_page - 1
        # 表格的行数
        row = 0
        col = 0
        # 判断页数是否合法
        if current_page > len(self.tab5_displayRes) - 1:
            # 超过最大页数
            self.__c_win_opt.OneBtnMsgBox("注意", "超过最大页数", QMessageBox.Information)
            self.PageQuery(int(self.current_page_2.text()) - 1, tableWidget)
            return
        elif current_page < 0:
            # 超过最大页数
            self.__c_win_opt.OneBtnMsgBox("注意", "小于最小页数", QMessageBox.Information)
            return
        # 进行填充
        res = self.tab5_displayRes[current_page]
        for x in res:
            path = CONFIG["@client_config"]["error_image_path"] + x[0].replace(":", "_") + '.jpg'
            widget = self.labelForRow(path)
            # 越界判断
            if col >= tableWidget.columnCount():
                col = 0
                row += 1
            tableWidget.setCellWidget(row, col, widget)
            col += 1

    # 取消提交
    def SlotCancelSubmit(self):
        """
        取消提交
        :return:
        """
        if not self.__c_win_opt.TwoBtnMsgBox("信息", "是否确认取消提交", QMessageBox.Information):
            return
        self.btn_screenshoot.show()
        self.btn_screenshoot_yes.hide()
        self.btn_screenshoot_no.hide()
        self.Cam_Opt.Start()

    # 确认递交
    def SlotSubmit(self):
        """
        槽函数: 确认提交
        :return:
        """
        # 提取被点击过的按钮列表
        token_list = [self.face_local[x][4] for x in self.click_Num if self.click_Num[x]]
        if len(token_list) == 0:
            self.__c_win_opt.OneBtnMsgBox("信息", "您未点击任何错误图片", QMessageBox.Information)
            return
        picture = [self.face_pic[x] for x in self.click_Num if self.click_Num[x]]
        time_list = []
        path = ""
        # 保存图片
        for x in picture:
            # 获取时间
            now_time = datetime.now().strftime('%F %T')
            time_list.append(now_time)
            path = CONFIG["@client_config"]["error_image_path"] + now_time + '.jpg'
            # 将":"换成_
            path = path.replace(':', '_')
            # 保存图片
            cv2.imwrite(path, x)
        # 合并列表, 写入数据库
        z = list(zip(time_list, token_list))
        res = self.__c_sqlite_opt.execute("INSERT INTO error_record_table (error_time, error_type) values (?,?);", z)
        if res:
            self.__c_win_opt.OneBtnMsgBox("信息", "错误数据添加成功", QMessageBox.Information)
        else:
            self.__c_win_opt.OneBtnMsgBox("信息", "错误数据添加失败, 请检查数据库设置", QMessageBox.Information)
            os.remove(path)
        # 控件操作
        self.btn_screenshoot.show()
        self.btn_screenshoot_yes.hide()
        self.btn_screenshoot_no.hide()
        # 清除所有的btn
        for x in self.btn_dict:
            self.btn_dict[x].deleteLater()
        # 启动相机
        self.Cam_Opt.Start()

    # 识别错误截取
    def SlotScreenShot(self):
        """
        错误信息识别
        :return:
        """
        # 先判断是否有数据
        if self.label_pic_3.pixmap() is None:
            self.__c_win_opt.OneBtnMsgBox("警告", "请先打开相关的摄像头或视频文件", QMessageBox.Warning)
            return
        # 暂停播放获取人脸框
        self.Cam_Opt.Stop()
        if not self.__c_win_opt.TwoBtnMsgBox("警告", "是否确认进行错误采集(采集方式:点击出错的人脸后提交)",
                                             QMessageBox.Information):
            self.Cam_Opt.Start()
            return
        # 获取数据
        self.face_pic, self.face_local = self.Cam_Opt.GetFacePicInfo()
        if len(self.face_pic) == 0:
            self.__c_win_opt.OneBtnMsgBox("警告", "截获的图片中未检测到人脸!", QMessageBox.Warning)
            self.Cam_Opt.Start()
            return
        # 生成相关变量
        self.click_Num = {}
        self.btn_dict = {}
        for x in range(len(self.face_pic)):
            self.click_Num[x] = False
        # 获取label控件的位置
        x = self.label_pic_3.geometry().x()
        y = self.label_pic_3.geometry().y()
        for flag in range(len(self.face_pic)):
            x1 = self.face_local[flag][0]
            y1 = self.face_local[flag][1]
            x2 = self.face_local[flag][2]
            y2 = self.face_local[flag][3]
            size_x = x2 - x1
            size_y = y2 - y1
            self.btn_dict[flag] = QPushButton(self.tab_4)
            self.btn_dict[flag].setStyleSheet('''background: transparent''')
            self.btn_dict[flag].move(x + x1 + 15, y + y1 + 10)
            self.btn_dict[flag].setFixedSize(size_x, size_y)
            self.btn_dict[flag].clicked.connect(lambda: self.BtnClicked(flag))
            self.btn_dict[flag].setVisible(True)
            self.btn_dict[flag].setIconSize(QSize(size_x / 3, size_y / 3))
        # 隐藏按钮
        self.btn_screenshoot.hide()
        self.btn_screenshoot_yes.show()
        self.btn_screenshoot_no.show()

    def BtnClicked(self, num):
        if self.click_Num[num]:
            self.click_Num[num] = False
            self.btn_dict[num].setIcon(QIcon())
        else:
            self.click_Num[num] = True
            # 将按钮绘制成打勾标识
            # self.btn_dict[num].setStyleSheet('''background: transparent;''')
            # border-image: url("ui_file/resource/icon/打勾_有圈.png")'''
            self.btn_dict[num].setIcon(QIcon(QPixmap('ui_file/resource/icon/提醒,感叹号_jurassic.png')))

    # 确定
    def SlotDecide(self):
        # 判断学号和名称是否合法
        if self.edit_std_id.text() == "" or self.edit_std_name.text() == "":
            self.__c_win_opt.OneBtnMsgBox("警告", "请先输入学号和姓名", QMessageBox.Warning)
            return

        # 捕获图片
        if self.btn_open_cam.text() == "确认捕获":
            self.SlotOpenCam()

        # 判断是否有照片
        if self.__output_res == []:
            self.__c_win_opt.OneBtnMsgBox("警告", "请先捕获或上传图片", QMessageBox.Warning)
            return

        # 传输数据, 判断该学号下有无人脸, 是否需要进行更新
        select_obj = {
            # 条件字段
            'stu_id': int(self.edit_std_id.text()),
            'where_list': ['stu_id', 'stu_status=normal'],
            'select_list': ['stu_name']
        }
        res = self.__c_db_opt.Db_Selete("stu_table", data=select_obj)
        if len(res) != 0:
            if res[0][0] != self.edit_std_name.text():
                # 查询结果出现问题
                self.__c_win_opt.OneBtnMsgBox("警告", "数据库查到该学号, 但姓名出错, 请检查后重试", QMessageBox.Warning)
                return
            if self.__c_win_opt.TwoBtnMsgBox("警告", "数据库已存在该学生照片, 是否更新覆盖", QMessageBox.Warning):
                self.UpdateStuInfo()
        else:
            # 无数据
            if self.__c_win_opt.TwoBtnMsgBox("注意", "是否确认添加该信息", QMessageBox.Information):
                self.AddStuInfo()

    def UpdateStuInfo(self):
        # 数据库状态更新
        sql = "update stu_table set stu_status='normal' where stu_id=" + self.edit_std_id.text() + ';'
        self.__c_db_opt.Db_Update_SQL(sql)
        res = self.__c_ai_face.FaceUpdate(self.edit_std_id.text(), self.__output_res)
        # 进行结果判断
        if not res:
            self.__c_win_opt.OneBtnMsgBox("警告", "AI更新人脸数据失败", QMessageBox.Warning)
        else:
            self.__c_win_opt.OneBtnMsgBox("成功", "AI更新人脸数据成功", QMessageBox.Information)
            # 将图片保存
            path = CONFIG["@client_config"]["stu_face"] + self.edit_std_id.text() + '.jpg'
            cv2.imwrite(path, self.__output_res)

    def AddStuInfo(self):
        # 调用百度API添加数据
        res = self.__c_ai_face.FaceAdd(self.edit_std_id.text(), self.__output_res)
        # 进行结果判断
        if res:
            # 插入数据数据库
            insert_obj = {'stu_id': int(self.edit_std_id.text()),
                          'stu_name': self.edit_std_name.text(),
                          'stu_status': "normal"}
            if not self.__c_db_opt.Db_Insert("stu_table", data=insert_obj):
                self.__c_win_opt.OneBtnMsgBox("警告", "数据库添加失败, 请检查数据是否合法!", QMessageBox.Warning)
                # 百度AI进行回滚操作
                if not self.__c_ai_face.FaceDelete(self.edit_std_id.text(), res):
                    self.__c_win_opt.OneBtnMsgBox("警告", "百度AI数据回滚失败, 请自行删除!", QMessageBox.Warning)
                return
            else:
                self.__c_win_opt.OneBtnMsgBox("信息", "添加人脸数据成功!", QMessageBox.Information)
                # 将图片保存
                path = CONFIG["@client_config"]["stu_face"] + self.edit_std_id.text() + '.jpg'
                cv2.imwrite(path, self.__output_res)
        else:
            self.__c_win_opt.OneBtnMsgBox("警告", "百度AI添加数据失败", QMessageBox.Warning)

    # 打开图片文件
    def SlotOpenFile(self):
        img_name, img_type = QFileDialog.getOpenFileName(self, "选择照片文件", "/",
                                                         "所有文件(*);;jpg文件(*.jpg);;png文件(*.png);;jpeg文件(*.JPEG)")
        if (img_name != ""):
            pic = QtGui.QPixmap(img_name).scaled(self.label_pic.width(), self.label_pic.height())
            self.label_pic.setPixmap(pic)
            # 人脸识别
            if not self.HaveFaceDet():
                self.__output_res = []
                self.label_pic.clear()
        else:
            self.__c_win_opt.OneBtnMsgBox("警告", "您未选择文件", QMessageBox.Warning)

    # 打开视频文件
    def SlotOpenVideoFile(self, label, ai_switch=True, class_mode=False):
        video_name, video_type = QFileDialog.getOpenFileName(self, "选择视频文件", "/",
                                                             "所有文件(*);;mp4文件(*.mp4);;mov文件(*.mov);;rm文件(*.rm)")
        print(ai_switch, class_mode)
        if (video_name != ""):
            self.Cam_Opt.ThreadOptShowVideo(video_name, label, ai_switch, class_mode)
        else:
            self.Cam_Opt.OneBtnMsgBox("警告", "您未选择文件", QMessageBox.Warning)

    # 打开摄像头文件进行头像标注
    def SlotOpenCamCheck(self, label, ai_switch=True, class_mode=False):
        label.clear()
        self.Cam_Opt.ThreadOptShowVideo("", label, ai_switch, class_mode)

    # 窗口最小化
    def SlotMiniWin(self):
        if self.isMinimized:
            self.showMinimized()
        else:
            self.showNormal()

    # 关闭窗口
    def SlotClose(self):
        print(1)
        if self.__c_win_opt.TwoBtnMsgBox("警告", "是否确认退出程序", QMessageBox.Warning):
            exit(1)

    # 打开本地摄像头
    def SlotOpenCam(self):
        if self.btn_open_cam.text() == "确认捕获":
            self.Cam_Opt.SavePic()
            self.__c_win_opt.OneBtnMsgBox("信息", "捕获成功", QMessageBox.Information)
            self.btn_open_cam.setText("重新捕获照片")
            # 人脸识别, 失败则重试
            if not self.HaveFaceDet():
                self.__output_res = []
                self.SlotOpenCam()
        elif self.btn_open_cam.text() == "重新捕获照片":
            self.Cam_Opt.ThreadOptShowVideo("", self.label_pic, False)
            self.btn_open_cam.setText("确认捕获")

        elif self.__c_win_opt.TwoBtnMsgBox("警告", "请注意, 打开摄像头会覆盖本地照片", QMessageBox.Warning):
            self.Cam_Opt.ThreadOptShowVideo("", self.label_pic, False)
            self.btn_open_cam.setText("确认捕获")

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

    # 进行脸部探测
    def HaveFaceDet(self):
        # 检查是否有人脸
        self.__output_res = []
        self.__output_res = self.ForFaceJudge(self.label_pic.pixmap())
        if len(self.__output_res) == 0:
            return False
        return True

    # 脸部检测判断
    def ForFaceJudge(self, pixmap):
        self.__c_win_opt.OneBtnMsgBox("提示", "进行人脸检测", QMessageBox.Information)
        # 人脸识别
        frame_img = self.__c_win_opt.QPixmapToMat(pixmap)
        face_res = self.__c_face_detect.FaceDetection(frame_img)
        input_pic = []
        # 判断识别结果
        if len(face_res) == 1:
            self.__c_win_opt.OneBtnMsgBox("提示", "人脸检测成功", QMessageBox.Information)
            input_pic = face_res[0]
        elif len(face_res) > 1:
            self.__c_win_opt.OneBtnMsgBox("注意:", "检测到多张人脸, 请重试", QMessageBox.Warning)
        else:
            self.__c_win_opt.OneBtnMsgBox("错误:", "没有检测出人脸, 请调整角度,避免遮挡后重试", QMessageBox.Critical)
        return input_pic
