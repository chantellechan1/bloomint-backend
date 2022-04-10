from flask import current_app
from enum import Enum
import jwt
import datetime
import time
import os


def get_flask_env():
    global FlaskEnv

    class FlaskEnv(Enum):
        PRODUCTION = 1
        DEVELOPMENT = 2
        TEST = 3

    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'test':
        return FlaskEnv.TEST
    elif flask_env == 'development':
        return FlaskEnv.DEVELOPMENT
    elif flask_env == 'production':
        return FlaskEnv.PRODUCTION
    else:
        # default to development,
        # it's safe
        return FlaskEnv.DEVELOPMENT


def try_get_user_email(request) -> str:
    jwt_token = request.headers.get('Authorization').split()[1].strip('"')
    jwt_payload = jwt.decode(jwt_token,
                             key=current_app.config['JWT_SECRET'],
                             algorithms=[current_app.config['JWT_ALG']])
    email = jwt_payload['email']
    return email


def create_jwt(email: str, timediff: datetime.timedelta) -> str:
    current_datetime = datetime.datetime.utcnow()
    expiry_datetime = current_datetime + timediff
    unix_expiry_datetime = time.mktime(expiry_datetime.timetuple())
    payload = {
        'email': email,
        'exp': unix_expiry_datetime
    }
    encoded_jwt = jwt.encode(
        payload=payload,
        key=current_app.config['JWT_SECRET'],
        algorithm=current_app.config['JWT_ALG'])
    return encoded_jwt


def get_base_address() -> str:
    flask_env = get_flask_env()
    if flask_env == FlaskEnv.PRODUCTION:
        return current_app.config['BASE_ADDRESS']
    else:
        return 'localhost:5000'
