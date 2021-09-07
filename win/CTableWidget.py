from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class NewTableWidget(QtWidgets.QWidget):

    def __init__(self,lst):
        super().__init__()
        self.resize(800,300)
        self.hlayout = QtWidgets.QHBoxLayout(self)
        self.lst = lst
        self.newTableWidget()

    # 表格控件
    def newTableWidget(self):
        label7 = QtWidgets.QLabel('已添加:')
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(len(self.lst))
        self.tableWidget.setHorizontalHeaderLabels(self.lst)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 使列表自适应宽度
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)    # 设置tablewidget不可编辑
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)      # 设置tablewidget不可选中
        for i in range(3):
            self.tableWidget.setCellWidget(i, len(self.lst) - 1, self.buttonForRow())  # 在最后一个单元格中加入修改、删除按钮
        self.hlayout.addWidget(label7)
        self.hlayout.addWidget(self.tableWidget)

    def buttonForRow(self):
        widget = QtWidgets.QWidget()
        # 修改
        self.updateBtn = QtWidgets.QPushButton('修改')
        self.updateBtn.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')

        # 删除
        self.deleteBtn = QtWidgets.QPushButton('删除')
        self.deleteBtn.setStyleSheet(''' text-align : center;
                                    background-color : LightCoral;
                                    height : 30px;
                                    border-style: outset;
                                    font : 13px; ''')
        self.deleteBtn.clicked.connect(self.DeleteButton)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.updateBtn)
        hLayout.addWidget(self.deleteBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def DeleteButton(self):
        button = self.sender()
        if button:
        	# 确定位置的时候这里是关键
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            #self.tableWidget.removeRow(row)
            print(row)
