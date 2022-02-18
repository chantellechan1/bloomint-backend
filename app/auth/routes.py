from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import time
import jwt
from .. import create_session
from .. import utils
from . import models

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    req_body = request.get_json()
    email = req_body['email']
    password = req_body['password']
    try:
        db_session = create_session()
        user = db_session.query(models.User).filter(
            models.User.email == email and models.User.deleted_at is None).first()

        if user is None:
            raise Exception("Failed to find user")

        if check_password_hash(user.hashed_password, password + current_app.config['PEPPER']):
            current_datetime = datetime.datetime.utcnow()
            expiry_datetime = current_datetime + \
                current_app.config['JWT_TIME_DIFF']
            unix_expiry_datetime = time.mktime(expiry_datetime.timetuple())
            payload = {
                'email': email,
                'exp': unix_expiry_datetime
            }
            encoded_jwt = jwt.encode(
                payload=payload,
                key=current_app.config['JWT_SECRET'],
                algorithm=current_app.config['JWT_ALG'])

            res = current_app.make_response(
                ({'token': encoded_jwt}, current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
        else:
            res = current_app.make_response(
                ('Login Failed', current_app.config['HTTP_STATUS_CODES']['UNAUTHORIZED']))
    except:
        res = current_app.make_response(
            ('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res


@auth_blueprint.route('/auth/create_user', methods=['POST'])
def create_user():
    req_body = request.get_json()
    email = req_body['email']
    password = req_body['password']

    min_password_length = current_app.config['MIN_PASSWORD_LENGTH']
    max_password_length = current_app.config['MAX_PASSWORD_LENGTH']
    if len(password) < min_password_length or len(password) > max_password_length:
        res = current_app.make_response((f'Password length must be between {min_password_length} and {max_password_length}',
                                         current_app.config['BAD_REQUEST']))
        return res
    try:
        db_session = create_session()

        # TODO: check if user exists already
        # result = db_session.query(User).filter(User.email==email).first()

        # TODO: check password min/max length

        # create hashed password
        hashed_password = generate_password_hash(
            password + current_app.config['PEPPER'], salt_length=128)

        # make creation date
        create_date = datetime.datetime.utcnow()

        # create user object
        user = models.User(
            email=email, hashed_password=hashed_password, created_at=create_date)

        # add user to table
        db_session.add(user)

        # commit transaction
        db_session.commit()

        res = current_app.make_response(
            ('Success', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    except:
        res = current_app.make_response(
            ('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['BAD_REQUEST']))

    return res


@auth_blueprint.route('/auth/delete_user', methods=['POST'])
def delete_user():
    req_body = request.get_json()
    password = req_body['password']
    try:
        email = utils.try_get_user_email(request)

        db_session = create_session()
        user = db_session.query(models.User).filter(
            models.User.email == email).first()
        if user is None:
            raise Exception("Failed to find user")

        if user.deleted_at is not None:
            raise Exception("User already deleted")

        if not check_password_hash(user.hashed_password, password + current_app.config['PEPPER']):
            raise Exception("invalid password")

        user.deleted_at = datetime.datetime.utcnow()
        db_session.commit()

        res = current_app.make_response(
            ('Success', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    except:
        res = current_app.make_response(
            ('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['BAD_REQUEST']))
    return res
