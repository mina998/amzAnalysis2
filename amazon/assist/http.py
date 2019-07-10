import logging, requests
from fake_useragent import UserAgent


class Http(object):

    log = logging.getLogger(__name__)

    def session(self, proxies={}, cookies=None):

        headers = {'User-Agent': UserAgent(verify_ssl=False).chrome}

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

            self.log.warning('HTTP状态:[{}], {}'.format(code, url))

        except Exception as e: self.log.warning('错误信息:',e)

        return ''