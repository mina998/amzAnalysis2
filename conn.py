from os import path, sep
# Sqlite
SQLITE_DB_URI = '%sdata.db'% (sep.join(path.realpath(__file__).split(sep)[:-1])+sep)


# TOR设置

CONTROL_PORT = 9151  #切换控制端口
SOCKS5H_POST = 9150  #对外代理端口