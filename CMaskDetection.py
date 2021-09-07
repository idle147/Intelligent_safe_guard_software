from CMaskOpt import *
from CFaceDetection import *


class CMaskDetection():
    def __init__(self):
        """
        口罩识别检测
        """
        self.mask_opt = CMaskOpt()
        self.face_detection = CFaceDetection()

    def MaskDetect(self, img):
        """
        口罩检测
        :param img: 图片
        :return: 识别口罩的人脸图片, 坐标位置
        """
        # 读取口罩上的人脸
        face_pic = []
        face_local = []
        self.face_detection.FaceDetectionPicAndLocal(img, face_pic, face_local)
        # 每张人脸输入进去识别, 并绘图
        for x in range(len(face_pic)):
            res = self.mask_opt.UsingModel(face_pic[x])
            x1, y1, x2, y2 = face_local[x]
            if res == 1:
                # 没带口罩
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                face_local[x] = (x1, y1, x2, y2, 1)
            elif res == 0:
                # 带口罩
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                face_local[x] = (x1, y1, x2, y2, 0)
            else:
                print("模型加载出现错误!")
        # 返回识别的结果
        return face_pic, face_local
