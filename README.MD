洋葱网络访问版

a.#安装配置tor

    1. apt install tor

    #生成密码 生成你的密码 yourpassword 为定义的密码, 记下来生成的密码
    2. tor --hash-password yourpassword

    #编辑/etc/tor/torrc, 去掉下面行的注释
    3. ControlPort 9051

    #重启, 让ControlPort监听9051端口
    4. /etc/init.d/tor restart


b.# 其他配置

    #下载代码
    1. git clone https://github.com/mina998/amzAnalysis2.git

    #切换目录
    2. cd amzAnalysis2

    #安装依赖包
    3. pip3 install -r requirements.txt

    #考备数据库
    4. cp data.db.bak data.db

    #运行程序
    5. python3 manage.py >>/root/run.log 2>&1 &
       或者
       nohup python3 manage.py >> /root/run.log 2>&1 &

    
    #定时清理日志
    6. crontab -e
       输入 * * * * 6 echo > /root/run.log
    
       
       

如查出现 Missing dependencies for SOCKS support.
安装    pip3 install requests['socks']