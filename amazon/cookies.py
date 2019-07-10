from gevent import monkey
monkey.patch_all()

import gevent
from random import choice
from amazon.assist.http import Http


class Cookies(Http):


    def __call__(self, queue, zip=10001, debug=False):
        """
        # 初始化
        :param zip: 邮编
        :param queue: gevent Queue
        :param debug: 调式模式
        """
        self.__debug = debug
        self.__queue = queue
        self.__zip = zip

        while True:

            if self.__queue.full(): self.log.warning('Cookies池已满....')

            tasks = [gevent.spawn(self.__main_) for i in range(5)]

            gevent.joinall(tasks)



    def __main_(self):
        """
        # 主函数
        :return:
        """
        session = self.session()

        message = self.__get_(session)

        if self.__debug and message: self.log.warning(message)



    def __get_(self, session):
        """
        # 获取Cookie 1
        :param session: 会话链接
        :return:
        """
        urls = [
            'https://www.amazon.com/gp/goldbox?ref_=nav_cs_gb_azl',
            'https://www.amazon.com/b/ref=gc_surl_giftcards?node=2238192011',
            'https://www.amazon.com/ref=nav_logo',
            'https://www.amazon.com/gp/help/customer/display.html?nodeId=508510&ref_=nav_cs_help',
            'https://www.amazon.com/b/?_encoding=UTF8&ld=AZUSSOA-sell&node=12766669011&ref_=nav_cs_sell',
            'https://www.amazon.com/Outlet/b/?ie=UTF8&node=517808&ref_=sv_subnav_goldbox_3'
        ]

        self.client(session, choice(urls))

        if not session.cookies.get('session-id'): return 'Session ID 获取失败.'

        return self.__post_(session)



    def __post_(self, session):
        """
        # 获取Cookie 2
        :param session:
        :return:
        """
        url = 'https://www.amazon.com/gp/delivery/ajax/address-change.html'
        # 获取此页面设置的必要cookies
        data = {
            'locationType': 'LOCATION_INPUT',
            'zipCode': self.__zip,
            'storeContext': 'generic',
            'deviceType': 'web',
            'pageType': 'Gateway',
            'actionSource': 'glow'
        }
        self.client(session, url, method='POST', data=data)

        cookies = session.cookies

        ubid = session.cookies.get('ubid-main')

        if ubid:

            self.__queue.put(cookies)

            print('Ubid:', ubid)

        else: return 'ubid-main 获取失败.'





if __name__ == '__main__':

    from gevent.queue import Queue

    queue = Queue(5)

    oo = Cookies(queue, debug=True)

    oo.run()