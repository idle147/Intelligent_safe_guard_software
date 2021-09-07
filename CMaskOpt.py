import cv2
import numpy as np
import tflearn
from Global import CONFIG
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, fully_connected, dropout
from tflearn.layers.estimator import regression
from tflearn.layers.normalization import local_response_normalization


class CMaskOpt():
    def __init__(self):
        """
        构造函数, 进行模型的训练
        """
        self.IMAGE_SIZE = CONFIG["@mask_detection"]["IMAGE_SIZE"]
        self.MODEL_NAME = CONFIG["@mask_detection"]["model_name"]
        self.LEARNING_RATE = CONFIG["@mask_detection"]["LEARNING_RATE"]
        self.network = []
        self.model = []
        # 读取与获取模型
        self.modelStructure()
        self.ReadModel()

    def modelStructure(self):
        """
        模型的结构
        :return:
        """
        # 输入层 placeholder
        conv_input = input_data(shape=[None, self.IMAGE_SIZE, self.IMAGE_SIZE, 3], name="input")

        """ 第一层 卷积池化层"""
        # incoming, nb_filter输出高度, filter_size 卷积核大小
        self.network = conv_2d(conv_input, 96, 11, strides=4, activation="relu")  # 卷积
        self.network = max_pool_2d(self.network, 3, strides=2)  # 池化
        self.network = local_response_normalization(self.network)

        """ 第二层 卷积池化层"""
        self.network = conv_2d(self.network, 256, 5, activation="relu")  # 卷积
        self.network = max_pool_2d(self.network, 3, strides=2)  # 池化
        self.network = local_response_normalization(self.network)

        """ 第三层 三重卷积层"""
        self.network = conv_2d(self.network, 384, 3, activation='relu')
        self.network = conv_2d(self.network, 384, 3, activation='relu')
        self.network = conv_2d(self.network, 256, 3, activation='relu')
        self.network = max_pool_2d(self.network, 3, strides=2)
        self.network = local_response_normalization(self.network)

        """ 第四层 双重全连接层 """
        # incoming, n_units, activation='linear'
        self.network = fully_connected(self.network, 4096, activation='tanh')
        self.network = dropout(self.network, 0.5)
        self.network = fully_connected(self.network, 4096, activation='tanh')
        self.network = dropout(self.network, 0.5)

        """ 第五层 输出层 """
        self.network = fully_connected(self.network, 2, activation="softmax")  # 全连接层

        # 构建损失函数核优化器
        self.network = regression(self.network, placeholder='default', optimizer='momentum',  # 优化器
                                  loss='categorical_crossentropy',
                                  learning_rate=self.LEARNING_RATE)

    def ReadModel(self):
        """
        读取Model
        :return:无
        """
        self.model = tflearn.DNN(self.network, checkpoint_path='model_alexnet',
                                 max_checkpoints=1, tensorboard_verbose=2)
        self.model.load(self.MODEL_NAME, weights_only=True)

    def UsingModel(self, img):
        """
        使用模型, 输入图片, 判断有没有戴口罩
        :param img: 参数图片
        :return:
        """
        img_resize = cv2.resize(img, (self.IMAGE_SIZE, self.IMAGE_SIZE))
        img_resize = img_resize.reshape((-1, self.IMAGE_SIZE, self.IMAGE_SIZE, 3))
        num = self.model.predict(img_resize)  # 获取概率
        classify = np.argmax(num)  # 获取标签
        if classify == 0:
            return 0
        elif classify == 1:
            return 1
        else:
            print("Error: Masks cannot be identified")
            return -1

    @staticmethod
    def getScore(y_test, predict_test):
        """
        获取口罩识别结果的分值
        :param y_test: 测试结果
        :param predict_test: 预测结果
        :return: 无
        """
        correct = 0
        error = 0
        for i in range(len(y_test)):
            print(y_test[i])
            if (y_test[i] == predict_test[i]).all():
                correct += 1
            else:
                error += 1
        res = correct / len(y_test)
        print('Test accuracy:%.2f%%' % res)
