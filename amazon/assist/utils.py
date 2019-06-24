import datetime, re, time, sqlite3

from lxml import etree
from conn import SQLITE_DB_URI


class Tools():

    @staticmethod
    def current_time(str='%Y-%m-%d %H:%M:%S'):
        """
        获取当日期时间
        :param str: 日期时间格式
        :return: 日期时间
        """
        return datetime.datetime.now().strftime(str)

    @staticmethod
    def time_stamp_now(t=False):
        """
        获取当前时间戳
        :return:
        """
        if t: return int(time.time())
        return time.time()

    @staticmethod
    def next_time_stamp():
        """
        明天时间戳
        :return:
        """
        # 当天日期
        today    = datetime.date.today()
        # 明天日期
        tomorrow = today + datetime.timedelta(days=1)
        # 转为时间数组
        timeArray = time.strptime(str(tomorrow), "%Y-%m-%d")
        # 转为时间戳
        return int(time.mktime(timeArray))-3600





class Xpath():

    def __new__(cls, xpath, docment):
        """
        #
        :param xpath:
        :param docment:
        :return:
        """
        if docment:
            tree = etree.HTML(docment)
            cls.result = tree.xpath(xpath)
        else: cls.result = []
        return object.__new__(cls)


    def first(self, default=''):
        """
        # 获取第一个值
        :param default: 如果获取失败, 返回默认值
        :return:
        """
        if not self.result: return default
        return self.result[0]



class Rule():

    def __new__(cls, pattern, docment):
        """
        # 正则获取
        :param pattern: 正则表达式
        :param docment:
        :return:
        """
        cls.result = re.findall(pattern, docment)
        return object.__new__(cls)


    def first(self, default=''):
        """
        # 返回第一个值
        :param default: 获取失败, 返回默认值
        :return:
        """
        if not self.result: return default
        return self.result[0]



class Db(object):
    __instance = None
    sqlite_uri = SQLITE_DB_URI

    def execute(self, sql):
        """
        执行SQL语句
        :param sql:
        :return:
        """
        try:
            return self.__cur.execute(sql)
        except Exception as e: print('Sql语句错误:', e)

    def commit(self):
        self.__con.commit()

    def close(self):
        self.__con.close()

    def __new__(cls, *args, **kwargs):
        """
        单例模式
        :param args:
        :param kwargs:
        :return:
        """
        if cls.__instance == None:
            cls.__con = sqlite3.connect(cls.sqlite_uri, timeout=60)
            cls.__cur = cls.__con.cursor()
            cls.__instance = object.__new__(cls)
        return cls.__instance

sqlite = Db()
