from flask import current_app
from flask.wrappers import Response, Request
from enum import Enum
from .auth import models as auth_models
from http import HTTPStatus
from typing import Callable
import logging
import jwt
import datetime
import time
import os


class FlaskEnv(Enum):
    PRODUCTION = 1
    DEVELOPMENT = 2
    TEST = 3


def get_flask_env() -> FlaskEnv:

    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'test':
        return FlaskEnv.TEST
    elif flask_env == 'development':
        return FlaskEnv.DEVELOPMENT
    elif flask_env == 'production':
        return FlaskEnv.PRODUCTION
    else:
        raise Exception("FLASK_ENV is not set")


def try_get_user_email(request) -> str:
    auth_tokens = request.headers.get('Authorization').split()
    if len(auth_tokens) != 2:
        raise Exception('Authorization failed, no bearer token')

    jwt_token = auth_tokens[1].strip('"')
    jwt_payload = jwt.decode(jwt_token,
                             key=current_app.config['JWT_SECRET'],
                             algorithms=[current_app.config['JWT_ALG']])
    email = jwt_payload['email']
    return email


def get_user_id_from_email(db_session, email) -> int:
    user = db_session.query(
        auth_models.User).filter(
        auth_models.User.email == email,
        auth_models.User.deleted_at == None).first()  # noqa
    user_id = user.id
    return user_id


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


def handle_api_request(api_function: Callable, request: Request) -> Response:
    """
    All the API calls should go through this function.
    It just does some generic logging and error handling

    """
    logger = logging.getLogger(__name__)
    try:
        logger.info("Received request {request}")
        return api_function(request)
    except Exception as e:
        # https://stackoverflow.com/questions/1483429/how-do-i-print-an-exception-in-python
        logger.warning(
            f"Error processing request {request}: {print(repr(e))}")
        return current_app.make_response(
            ('Something bad happened', HTTPStatus.BAD_REQUEST))
