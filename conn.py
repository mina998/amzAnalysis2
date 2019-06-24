from os import path, sep
# Sqlite
SQLITE_DB_URI = '%sdata.db'% (sep.join(path.realpath(__file__).split(sep)[:-1])+sep)