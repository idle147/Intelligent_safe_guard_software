import sys
from win.CStartWin import *
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_show = CStartWin()
    login_show.show()
    sys.exit(app.exec_())
