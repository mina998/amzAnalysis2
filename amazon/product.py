from gevent import monkey
from conn import CONTROL_PORT, SOCKS5H_POST

monkey.patch_all()
import json, gevent, random
from stem import Signal
from stem.control import Controller
from amazon.assist.http import Http
from amazon.assist.utils import Rule, Tools, sqlite, Xpath


class Product(Http):


    def __call__(self, queue, api='tor', debug=False):
        """
        # 运行
        :param queue: 多进程Queue对象
        :param api: 请求时使用的网络api [值:api=tor 连接到TOR网络, api=None 不使用代理, api='http://xxx.cop/ip' 使用api中的代理]
        :param debug: 请调模式
        :return:
        """
        self.__proxy = {'http':'socks5h://127.0.0.1:%d'%SOCKS5H_POST, 'https':'socks5h://127.0.0.1:%d'%SOCKS5H_POST}
        self.__debug = debug
        self.__queue = queue
        self.__api_  = api
        self.__proxie= ''

        if api == 'tor': self.__conncet_tor()
        elif not api: self.__proxy= None

        self.__run_()



    def __run_(self):
        """
        # 入口函数
        :return:
        """
        while True:


            asins = self.__asin_get()

            ids = [row[0] for row in asins]

            self.__status_up(ids, time=Tools.time_stamp_now(t=True))

            self.__proxy_change()

            tasks = [gevent.spawn(self.__main_, row) for row in asins]

            gevent.joinall(tasks)




    def __main_(self, row):
        """
        # 查询主函数
        :param tuple row:
        :return:
        """
        session = self.session(cookies=self.__queue.get(), proxies=self.__proxy)

        message = self.__get_(session, row)

        if message:

            self.__status_up(row[0])

            if self.__debug: self.log.warning(message+' '+self.__proxie)

        s = random.randint(1, 6)

        gevent.sleep(s)



    def __get_(self, session, row):
        """
        # 查询数据
        :param session:
        :return:
        """

        id, asin, seller = row
        # 主机
        link = 'https://www.amazon.com/dp/{}?m={}&th=1&psc=1'.format(asin, seller)
        # 发送请求
        html = self.client(session, link)

        if html == '': return '{}, 获取不到HTML.'.format(asin)

        elif 'Currently unavailable.' in html:

            self.__status_up(id, time=-1)

            self.log.warning('{}, 商品已下架.'.format(asin))

            return None

        elif 'Enter the characters you see below' in html: return '{}, 出现验证码.'.format(asin)


        return self.__parse(html, asin, id, session)



    def __parse(self, html, asin, id, session):
        """
        # 解析数据
        :param html:
        :param asin:
        :param session:
        :return:
        """
        rank = Rule(r"#([\d,]+?) in\s.*?See Top 100 in .*?</a>\)", html).first(default='0').replace(',', '')

        imge = Rule(r'colorImages\'.*?(https.*?)"', html).first()

        xpath  = '//*[@id="price_inside_buybox" or @id="priceblock_ourprice"]/text()'
        price = Xpath(xpath, html).first().replace('$','')
        if not price: return '{}, 价格获取失败.'.format(asin)

        stock = Rule(r'Only (\d+?) left in stock - order soon.', html).first()
        if not stock: stock = self.__post_(session, asin)
        if not stock.isdigit(): return stock

        self.__save_(price=price, stock=stock, rank=rank, imge=imge, asin=asin, id=id)



    def __post_(self, session, asin):
        """
        # POST 查询库存
        :param session:
        :param asin:
        :return:
        """
        data = {'ASIN': asin, 'verificationSessionID': session.cookies.get('session-id'), 'quantity': '999'}
        #Post地址
        link = 'https://www.amazon.com/gp/add-to-cart/json/ref=dp_start-bbf_1_glance'
        #开始发送

        code = self.client(session, link, method='POST', data=data)

        stock= json.loads(code.strip())

        if stock.get('isOK'): return stock.get('cartQuantity') or '1'

        return '{}, {}'.format(asin, stock.get('exception').get('reason'))



    def __save_(self, price, stock, rank, imge, asin, id):
        """
        # 保存并更新数据
        :param price:
        :param stock:
        :param rank:
        :param imge:
        :param asin:
        :param id:
        :return:
        """
        sql = 'insert into marks (price,stock,bsr,uptime,asin_id) values ({},{},{},datetime("now","localtime"),{})'.format(price,stock,rank,id)
        sqlite.execute(sql)

        sql = 'update listing set img = "{}" where id={}'.format(imge, id)
        sqlite.execute(sql)

        sqlite.commit()

        print('{}, 库存:{}, 价格:{}, 排名:{}. {}'.format(asin, stock.rjust(3), price.rjust(6), rank.rjust(7), self.__proxie))


    #
    def __status_up(self, ids, time=0):
        """
        # 更新状态
        :param ids:
        :param int time: 时间戳
        :return:
        """

        if isinstance(ids, list): ids = ','.join([str(id) for id in ids])

        sql = 'update listing set status ={} where id in ({})'.format(time, ids)

        sqlite.execute(sql)

        sqlite.commit()



    def __asin_get(self):

        # 每次查询几香槟酒
        num = random.randint(3, 8)
        # 每天早上8点时间戳
        exe = 'strftime("%s","now", "start of day")'
        sql = 'select id,asin,seller from listing where status < {} and status > -1 order by random() limit {}'.format(exe, num)


        while True:

            res =  sqlite.execute(sql).fetchall()

            if res: return res

            print('等侍下次抓取......')

            gevent.sleep(10)



    def __proxy_change(self):

        """
        # 切换代理IP
        :return:
        """

        if self.__api_.startswith('http'):

            text = self.session().get(self.__api_).text

            self.__proxy = json.loads(text)

            self.__proxie = self.__proxy.get('http')


        try:
            if isinstance(self.__tor_control, Controller):

                self.__tor_control.signal(Signal.NEWNYM)  # 更新IP

                if self.__debug:

                    text = self.session(proxies=self.__proxy).get('https://api.ipify.org?format=json').text

                    self.__proxie = json.loads(text).get('ip')

                else: self.__proxie = 'tor proxies.'

        except Exception as e: exit('切换代理失败:{}'.format(e))



    def __conncet_tor(self):
        """
        # 连接到TOR网络
        :return:
        """
        try:
            # 注意端口 容易引起连接失败.
            controller = Controller.from_port(port=CONTROL_PORT)

            controller.authenticate()

            self.__tor_control = controller

        except Exception as e: exit('TOR链接失败: {}'.format(e))






if __name__ == '__main__':

    from gevent.queue import Queue

    queue = Queue(5)

    oo = Product(debug=True)

    oo.run(queue)