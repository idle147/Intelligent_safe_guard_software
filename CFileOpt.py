class CFileOpt():
    @staticmethod
    def readQss(path):
        """
        读取QSS文件
        :param path: QSS文件的路径
        :return:
        """
        with open(path) as f:
            qss = f.read()
        f.close()
        return qss
