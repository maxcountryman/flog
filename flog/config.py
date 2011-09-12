class Config(object):
    SECRET_KEY = '#\xfa\xaas\\\xf1\xbc\xd8\xf8\x05*\xa5\x80\x9e!f'
    
    SITE_NAME = 'Flog'
    SITE_TITLE = 'A simple Flask blog | ' + SITE_NAME
    SITE_AUTHOR = 'A Python Blogger'
    SITE_DESCRIPTION = 'A blog written in Python with Flask!'
    LONG_DESCRIPTION = 'This is a little blog written with a little web ' \
    'framework called Flask, written with simplicity in mind. Flog is ' \
    'designed to be extended to meet your needs.'
    
    GOOGLE_ANALYTICS_UA = 'change me!' 
    
    POSTS_PER_PAGE = 3
    
    SITE_WHITELIST = ['127.0.0.1']


class ConfigDebug(Config):
    DEBUG = True
    EXTERNAL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/flog.db'


class ConfigProduction(Config):
    DEBUG = False
    EXTERNAL = True
    EXTERNAL_HOST = '192.168.0.1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flog.db'

