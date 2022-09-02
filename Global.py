from CFaceDetection import CFaceDetection
from CFileOpt import CFileOpt
import json

print("Global运行次数....")


# 照片参数
IMAGE_SIZE = 150  # 表示图片的大小

# 背景图片
BACKGROUND_PATH = "./ui_file/resource/img/background5.jpg"

# 样式设计
QSS = CFileOpt().readQss("ui_file/resource/qss_file/QPushbtn.qss")
CORRECT_PIC = "ui_file/resource/icon/打勾_有圈.png"
ERROR_PIC = "ui_file/resource/icon/提醒,感叹号_jurassic.png"

with open("./config/config.json", "r") as File:
    print("读取Json文件")
    CONFIG = json.loads(File.read())
# 基本参数设置
LOGIN = 101
REGISTER = 102
KEEP_ALIVE = 110

# 获取FaceDetection
face_detection = CFaceDetection()
