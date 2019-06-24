import requests
from fake_useragent import UserAgent


class Http(object):




    def session(self, proxies={}, cookies=None):

        headers = {'User-Agent': UserAgent().chrome}

        session = requests.session()

        session.headers.update(headers)

        session.proxies=proxies

        if cookies: session.cookies=cookies

        return session




    def client(self, session, url, method='GET', data=None):

        try:

            result = session.request(method, url, data=data)

            code = result.status_code

            if code in [200, 201]: return result.text

            print('HTTP状态:[{}], {}'.format(code, url))

        except Exception as e: print('错误信息:',e)

        return ''