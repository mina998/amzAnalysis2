from flask import Blueprint

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ams = Blueprint(
    'ams',
    __name__,
    static_folder='assets',
    template_folder='templates'
)

from . import views