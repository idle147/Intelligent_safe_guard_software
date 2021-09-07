from Global import CONFIG


# 获取服务器相关设置信息
def GetClientConf(info):
    return CONFIG["@client_config"][info]


# 获取百度API相关信息
def GetBaiDuConf(info):
    return CONFIG["@baidu_api"][info]


# 获取mysql相关信息
def GetMysqlConf(info):
    return CONFIG["@mysql_opt"][info]


# 获取mode相关信息
def GetModelConf(info):
    return CONFIG["@mask_detection"][info]
