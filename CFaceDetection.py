import cv2
import numpy as np


class CFaceDetection():
    def __init__(self):
        """
        OpenCv2 人脸检测级联分类器, 用以识别图像内是否有人脸
        """
        self.face_cascade = cv2.CascadeClassifier(r'config/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(r'config/haarcascade_eye.xml')

    @staticmethod
    def QpixmapToCvImg(qtpixmap):
        """
        将Pixmap转成Cv图像
        :param qtpixmap: pixmap图像
        :return: 转成cv图像的结果
        """
        qimg = qtpixmap.toImage()
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        return result

    # 人脸识别
    def FaceDetection(self, img):
        """
        人脸检测
        :param img: 人脸图片
        :return: 人脸检测的结果
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = self.Detect(gray)
        res = []
        if len(rects) > 0:  # 大于零检测人脸
            res.extend(img[y1:y2, x1:x2] for x1, y1, x2, y2 in rects)
        return res

    def FaceDetectionPicAndLocal(self, img, face_pic, face_local):
        """
        在人脸检测的基础上, 加上了坐标定位
        :param img:  图片
        :param face_pic: 需要保存人脸的 list
        :param face_local:  需要保存人脸位置的 list
        :return: 无
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = self.Detect(gray)
        if len(rects) > 0:  # 大于零检测人脸
            for x1, y1, x2, y2 in rects:
                crop = img[y1:y2, x1:x2]
                face_pic.append(crop)
                face_local.append((x1, y1, x2, y2))

    def Detect(self, img):
        """
        人脸检测
        :param img: 图片
        :return: 检测的结果
        """
        rects = self.face_cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30))
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects
