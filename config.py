import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = 'postgresql:///rova'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

