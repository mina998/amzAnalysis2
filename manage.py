from multiprocessing import Process, Queue
from amazon.cookies import Cookies
from amazon.product import Product
from web.app import app


debug = True

def service():

    app.debug = debug
    app.run(host='0.0.0.0',port=1081)




if __name__ == '__main__':


    queue = Queue(maxsize=60)

#运行WEB服务器
    t0 = Process(target=service)
    t0.start()


#获取COOKIES
    kwargs = dict(queue=queue, zip=10001, debug=0)
    t1 = Process(target=Cookies(), kwargs=kwargs)
    t1.start()


#抓取数据
    kwargs = dict(queue=queue, api='tor', debug=debug)
    t2 = Process(target=Product(), kwargs=kwargs)
    t2.start()


