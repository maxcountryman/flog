class Config(object):
    # site settings
    SITE_NAME = 'Blog'
    POSTS_PER_PAGE = 4
    SECRET_KEY = '#\xfa\xaas\\\xf1\xbc\xd8\xf8\x05*\xa5\x80\x9e!f'
    
    # database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/flog.db'


class ConfigDebug(Config):
    DEBUG = True
    EXTERNAL = False


class ConfigProduction(Config):
    DEBUG = False
    EXTERNAL = True
    EXTERNAL_HOST = '192.168.0.1'

