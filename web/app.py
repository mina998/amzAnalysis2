from flask import Flask
from conn import SQLITE_DB_URI
from web import db, ams


app = Flask(__name__, static_folder='')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % SQLITE_DB_URI
app.config['SECRET_KEY'] = 'ce2c0c02d6d8413782794451788ffa7f'

db.init_app(app)

app.register_blueprint(ams)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=1082)