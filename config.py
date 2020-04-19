import configparser, json
from datetime import timedelta
from functools import wraps

cfg = configparser.ConfigParser()
cfg.read('config.cfg')

class Config():
    SQLALCHEMY_DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (
        cfg['database']['default_connection'],
        cfg['mysql']['driver'],
        cfg['mysql']['user'],
        cfg['mysql']['password'],
        cfg['mysql']['host'],
        cfg['mysql']['port'],
        cfg['mysql']['db']
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_SECRET_KEY = cfg['jwt']['secret_key']
    X_HOST = cfg['amazon']['x_host']
    X_APIKEY = cfg['amazon']['x_apikey']
    
# class DevelopmentConfig(Config):
#     APP_DEBUG = True
#     DEBUG = True
#     MAX_BYTES = 10000
#     APP_PORT = 9090

# class ProductionConfig(Config):
#     APP_DEBUG = False
#     DEBUG = False
#     MAX_BYTES = 10000
#     APP_PORT = 5050