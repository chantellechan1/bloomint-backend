import datetime
from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .. import create_session
from .. import utils
from .. import emailer
from . import models
from http import HTTPStatus

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

        if check_password_hash(user.hashed_password,
                               password + current_app.config['PEPPER']):
            encoded_jwt = utils.create_jwt(
                email=email,
                timediff=current_app.config['JWT_LOGIN_EXPIRY'])

            res = current_app.make_response(
                ({'jwt': encoded_jwt}, HTTPStatus.OK))
        else:
            res = current_app.make_response(
                ('Login Failed', HTTPStatus.UNAUTHORIZED))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res


@auth_blueprint.route('/auth/create_user', methods=['POST'])
def create_user():
    """ The first step to creating a user.
    If successful, this ends with an email being
    sent to the provided email which contains
    a verification link.

    We don't ask for the password yet, they need to get past
    email verification first
    """
    req_body = request.get_json()
    email = req_body['email']
    try:
        db_session = create_session()

        # check if user exists already
        existing_user = db_session.query(
            models.User).filter(
            models.User.email == email).first()
        if existing_user is not None:
            res = current_app.make_response((f'user with email {email} already exists',
                                             HTTPStatus.BAD_REQUEST))
            return res

        # send them the email with the jwt
        jwt = utils.create_jwt(
            email=email,
            timediff=current_app.config['JWT_EMAIL_VERIFICATION_EXPIRY'])

        if utils.get_flask_env() == utils.FlaskEnv.TEST:
            # When we run the test, it's too painful to set up the email stuff.
            # Just return the jwt in the response so they confirm their email
            # address and set their password
            res = current_app.make_response(
                ({'jwt': jwt}, HTTPStatus.OK))
        else:
            emailer.send_email("Bloomint verification email",
                               f"Click this link to verify your \
                               email address: {utils.get_base_address()}/static/authorize?jwt={jwt}",
                               email)

            res = current_app.make_response(
                ('Success', HTTPStatus.OK))
    except BaseException as e:
        print(e.args)
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))

    return res


@auth_blueprint.route('/auth/verify_user', methods=['POST'])
def verify_user():
    """ Confirm the users email is legit,
    grab their password here,
    and finally add the new user into the database.
    """
    try:
        req_body = request.get_json()
        password = req_body['password']
        email = utils.try_get_user_email(request)

        min_password_length = current_app.config['MIN_PASSWORD_LENGTH']
        max_password_length = current_app.config['MAX_PASSWORD_LENGTH']
        if len(password) < min_password_length or len(
                password) > max_password_length:
            res = current_app.make_response((f'Password length must be between {min_password_length} and {max_password_length}',
                                             HTTPStatus.BAD_REQUEST))
            return res

        db_session = create_session()

        # check if user exists already
        # we check again here. It's unlikely
        # but possible that someone took the email between
        # the time we sent the verification email, and the time
        # they actually click it and end up here.
        existing_user = db_session.query(
            models.User).filter(
            models.User.email == email).first()
        if existing_user is not None:
            res = current_app.make_response((f'user with email {email} already exists',
                                             HTTPStatus.BAD_REQUEST))
            return res

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
            ('Successfully registered user with password', HTTPStatus.OK))
        return res
    except BaseException as e:
        print(e.args)
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return None


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

        if not check_password_hash(
                user.hashed_password, password + current_app.config['PEPPER']):
            raise Exception("invalid password")

        user.deleted_at = datetime.datetime.utcnow()
        db_session.commit()

        res = current_app.make_response(
            ('Success', HTTPStatus.OK))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res


@auth_blueprint.route('/auth/get_user', methods=['GET'])
def get_user():
    try:
        email = utils.try_get_user_email(request)

        db_session = create_session()
        user = db_session.query(models.User).filter(
            models.User.email == email).first()

        res = current_app.make_response(
            ({
                'email': user.email,
                'created_at': user.created_at
            }, HTTPStatus.OK))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res
