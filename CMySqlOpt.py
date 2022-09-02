# *coding:utf-8 *
from Global import CONFIG
import pymysql


class CDbOpt:
    def __init__(self):
        """
        MySql操纵类函数的相关初始化数值
        """
        self.conn_mysql = pymysql.Connect(
            database=CONFIG["@mysql_opt"]["mysql_db"],
            user=CONFIG["@mysql_opt"]["mysql_user"],
            password=CONFIG["@mysql_opt"]["mysql_pwd"],
            host=CONFIG["@mysql_opt"]["mysql_host"],
            port=CONFIG["@mysql_opt"]["mysql_port"],
            charset=CONFIG["@mysql_opt"]["mysql_charset"],
        )

    def __del__(self):
        """
        析构函数: 关闭Sql连接
        """
        self.conn_mysql.close()

    def Db_Selete(self, *args, **kwargs):
        # 获取数据字段
        # 整理出sql
        # 调用db
        table = args[0]
        where_fields = ''
        data = kwargs.get('data')
        where_list = data.get('where_list')
        select_list = data.get('select_list')
        if where_list != None:
            del data['where_list']
        if select_list != None:
            del data['select_list']
        for k, v in data.items():
            if k in where_list:
                where_fields += f"{k}='{v}'" if where_fields == '' else f"and {k}='{v}'"
        fields = ','.join(select_list)

        cursor = self.conn_mysql.cursor()
        sql = f"""select {fields} from {table} where {where_fields}"""
        cursor.execute(sql)
        return cursor.fetchall()

    def Db_SELECT_SQL(self, sql):
        # 获取数据字段
        # 整理出sql
        # 调用db
        cursor = self.conn_mysql.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def Db_Update_SQL(self, sql):
        # 调用sql
        cursor = self.conn_mysql.cursor()
        try:
            cursor.execute(sql)
            self.conn_mysql.commit()
            return True
        except Exception as e:
            print(e)
            self.conn_mysql.rollback()
            return False

    def Db_Update(self, *args, **kwargs):
        table = args[0]
        fields = ''
        where_fields = ''
        data = kwargs.get('data')
        where_list = data.get('where_list')
        select_list = data.get('select_list')
        if where_list != None:
            del data['where_list']
        if select_list != None:
            del data['select_list']
        for k, v in data.items():
            if k in where_list:
                where_fields += f"{k}='{v}'" if where_fields == '' else f"and {k}='{v}'"
            else:
                fields += f"{k}='{v}'" if fields == '' else f", {k}='{v}'"
        # 调用sql
        cursor = self.conn_mysql.cursor()
        sql = f"""update {table} set {fields} where {where_fields}"""
        try:
            cursor.execute(sql)
            self.conn_mysql.commit()
        except Exception as e:
            print(e)
            self.conn_mysql.rollback()


    def Db_Insert(self, *args, **kwargs):
        table = args[0]
        fields = ''
        where_fields = ''
        data = kwargs.get('data')
        where_list = data.get('where_list')
        select_list = data.get('select_list')
        if where_list != None:
            del data['where_list']
        if select_list != None:
            del data['select_list']
        for num, (k, v) in enumerate(data.items()):
            if num == 0:
                where_fields += f"{k}"
                fields += f"'{v}'"
            else:
                where_fields += f", {k}"
                fields += f", '{v}'"
        cursor = self.conn_mysql.cursor()
        sql = f"""insert into {table} ({where_fields}) values({fields})"""
        try:
            cursor.execute(sql)
            self.conn_mysql.commit()
            return True
        except Exception as e:
            print(e)
            self.conn_mysql.rollback()
            return False

    def Db_Delete(self, *args, **kwargs):
        table = args[0]
        fields = ''
        where_fields = ''
        data = kwargs.get('data')
        where_list = data.get('where_list')
        select_list = data.get('select_list')
        if where_list != None:
            del data['where_list']
        if select_list != None:
            del data['select_list']
        for k, v in data.items():
            fields += f"{k}='{v}'" if fields == '' else f", {k}='{v}'"
            if k in where_list:
                where_fields += f"{k}='{v}'" if where_fields == '' else f"and {k}='{v}'"
        cursor = self.conn_mysql.cursor()
        sql = f"""delete from {table} where {where_fields}"""
        try:
            cursor.execute(sql)
            self.conn_mysql.commit()
        except Exception as e:
            print(e)
            self.conn_mysql.rollback()
