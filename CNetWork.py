# encoding:utf-8
from Global import CONFIG
import requests


class CNetWork():
    def __init__(self):
        """
        判断百度AI服务器的连接状态, 同时也可以获取Token
        """
        "输入KEY的值"
        self.API_KEY = CONFIG["@baidu_api"]["API_KEY"]
        "输入SECRET_KEY的值"
        self.SECRET_KEY = CONFIG["@baidu_api"]["SECRET_KEY"]

    def ConnectCheck(self):
        """
        获取连接状态
        :return: 0: 正常连接, -2:APIkey不正确, -3:SecretKey不正确,  -4 异常错误
        """
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='
        host += f'{self.API_KEY}&client_secret={self.SECRET_KEY}'
        try:
            response = requests.get(host)
            if response.status_code != 200:
                return -1
            # 连接成功, 检查token
            re_json = response.json()
            if 'error' in re_json:
                return -2 if re_json['error_description'] == 'unknown client id' else -3
            return 0
        except:
            # 网络连接问题
            return -4
