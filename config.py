import datetime
import logging
import os


class Config(object):
    """
    Properties in here do not change between production and config
    """
    # days to JWT expiry after user logs in
    JWT_LOGIN_EXPIRY = datetime.timedelta(days=30)
    # minutes to JWT expiry after user is sent verification email
    JWT_EMAIL_VERIFICATION_EXPIRY = datetime.timedelta(minutes=10)

    JWT_ALG = 'HS256'
    NUM_HASH_ITERATIONS = 4096
    SALT_LENGTH = 128

    MAX_PASSWORD_LENGTH = 100
    MIN_PASSWORD_LENGTH = 7

    DB_ECHO = False

    LOG_FORMAT = '%(asctime)s-%(levelname)s:%(message)s'
    LOG_FILENAME = f'{os.getcwd()}/logs/log.txt'
    LOG_LEVEL = logging.INFO


class ProductionConfig(Config):
    PEPPER = ''
    JWT_SECRET = ''

    DB_PASSWORD = ''
    DB_HOST = ''
    DB_CONN_STRING = f''

    # email settings
    # If you are using real email, you need to find an smtp server you can use.
    # for example: smtp.gmail.com
    # default port for smtp is 465
    # sender email is ofc, who is sending this email
    # you're going to need SSL if its a real email server, and you will need to
    # use a password. When using gmail, I had to use an app password.
    # apparently with outlook you can directly log in with you email +
    # password combo
    SMTP_SERVER = ''
    SMTP_SERVER_PORT = 465
    SMTP_SENDER_EMAIL = ''
    SMTP_USE_SSL = True
    SMTP_SENDER_PASSWORD = ''

    # If you have a domain name put it here,
    # otherwise use the IP address of the server
    BASE_ADDRESS = ''


class DevelopmentConfig(Config):
    PEPPER = ''
    JWT_SECRET = ''

    DB_PASSWORD = ''
    DB_HOST = ''
    DB_CONN_STRING = f''

    # email settings
    SMTP_SERVER = ''
    SMTP_SERVER_PORT = 465
    SMTP_SENDER_EMAIL = ''
    SMTP_USE_SSL = True
    SMTP_SENDER_PASSWORD = ''


class TestConfig(Config):
    PEPPER = ''
    JWT_SECRET = ''

    DB_PASSWORD = ''
    DB_HOST = ''
    DB_CONN_STRING = f''
