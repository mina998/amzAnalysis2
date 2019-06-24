from gevent import monkey

monkey.patch_all()
import json, gevent, random,time
from stem import Signal
from stem.control import Controller
from amazon.assist.http import Http
from amazon.assist.utils import Rule, Tools, sqlite



class Product(Http):



    def __call__(self, queue, api='tor', debug=False):
        """
        # 运行
        :param queue: 多进程Queue对象
        :param api: 请求时使用的网络api [值:api=tor 连接到TOR网络, api=None 不使用代理, api='http://xxx.cop/ip' 使用api中的代理]
        :param debug: 请调模式
        :return:
        """
        self.__proxy = {'http':'socks5://127.0.0.1:9050', 'https':'socks5://127.0.0.1:9050'}
        self.__debug = debug
        self.__queue = queue
        self.__api_ = api

        if api == 'tor': self.__conncet_tor()
        elif not api: self.__proxy= None

        self.__run_()



    def __run_(self):
        """
        # 入口函数
        :return:
        """
        while True:

            # 如果没有内容, 等侍60秒
            if not sqlite.execute('select count(id) from listing').fetchone()[0]: gevent.sleep(60)

            # 下次执行剩余
            exe = Tools.next_time_stamp() - Tools.time_stamp_now(t=True)
            # 每次查询几香槟酒
            num = random.randint(3, 8)

            sql = 'select id,asin,seller from listing where status =0 order by random() limit {}'.format(num)

            res = sqlite.execute(sql).fetchall()

            if not res:

                if exe > 1:
                    print('倒计时: {}秒'.format(exe))
                    time.sleep(10)
                    continue

                sqlite.execute('update listing set status=0')
                sqlite.commit()


            ids = [row[0] for row in res]

            self.__status_up(ids, status=1)

            tasks = [gevent.spawn(self.__main_, row) for row in res]

            gevent.joinall(tasks)

            self.__proxy_change()



    def __main_(self, row):
        """
        # 主函数
        :return:
        """

        self.__text_proxies = self.__test_proxy()

        session = self.session(cookies=self.__queue.get(), proxies=self.__proxy)

        message = self.__get_(session, row)

        if message:

            self.__status_up(row[0])

            if self.__debug: print(message, self.__text_proxies)

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
        host = 'https://www.amazon.com'
        # URI
        link = host + '/dp/{}?m={}'.format(asin, seller) if seller else host + '/dp/' + asin
        # 发送请求
        html = self.client(session, link)

        if html == '': return '{}, 获取不到HTML.'.format(asin)

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

        price = Rule(r'id=\"priceblock_ourprice.*?>\$([\d.]+)<', html).first()
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
        data = {'ASIN': asin, 'verificationSessionID': session.cookies.get('session-id'), 'quantity': '99999'}
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
        sql = 'insert into marks (price,stock,bsr,uptime,asin_id) values ({},{},{},datetime("now"),{})'.format(price,stock,rank,id)
        sqlite.execute(sql)

        sql = 'update listing set img = "{}" where id={}'.format(imge, id)
        sqlite.execute(sql)

        sqlite.commit()

        print('{}, 库存:{}, 价格:{}, 排名:{}. {}'.format(asin, stock.rjust(3), price.rjust(6), rank.rjust(7), self.__text_proxies))


    #
    def __status_up(self, ids, status=0):
        """
        # 更新状态
        :param ids:
        :param status:
        :return:
        """

        if isinstance(ids, list):

            ids = ','.join([str(id) for id in ids])

        sql = 'update listing set status ={} where id in ({})'.format(status, ids)
        sqlite.execute(sql)

        sqlite.commit()



    def __proxy_change(self):

        """
        # 切换代理IP
        :return:
        """
        try:

            if self.__api_.startswith('http'):

                text = self.session().get(self.__api_).text

                self.__proxy = json.loads(text)

            if isinstance(self.__tor_control, Controller): self.__tor_control.signal(Signal.NEWNYM)  # 更新IP

        except Exception as e: exit('切换代理失败:{}'.format(e))





    def __conncet_tor(self):
        """
        # 连接到TOR网络
        :return:
        """
        try:
            # 注意端口 容易引起连接失败.
            controller = Controller.from_port(port=9051)

            controller.authenticate()

            self.__tor_control = controller

        except Exception as e: exit('TOR链接失败: {}'.format(e))



    def __test_proxy(self):
        """
        # 测试代理是否正常
        :return:
        """
        if self.__debug is False: return ''

        if self.__api_: return self.__proxy.get('http')

        # 查看TOR 代理
        try:
            text = self.session(proxies=self.__proxy).get('https://api.ipify.org?format=json').text

            return json.loads(text).get('ip')

        except Exception as e: print('TOR代理:', e)




if __name__ == '__main__':

    from gevent.queue import Queue

    queue = Queue(5)

    oo = Product(debug=True)

    oo.run(queue)