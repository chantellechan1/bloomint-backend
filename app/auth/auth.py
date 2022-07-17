from . import models
from werkzeug.security import generate_password_hash, check_password_hash
from flask.wrappers import Response, Request
from flask import current_app
from .. import create_session
from .. import utils
from .. import emailer
from http import HTTPStatus
import datetime


def login(request: Request) -> Response:
    req_body = request.get_json()
    email = req_body['email']
    password = req_body['password']

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

        return current_app.make_response(
            ({'jwt': encoded_jwt}, HTTPStatus.OK))
    else:
        return current_app.make_response(
            ('Login Failed', HTTPStatus.UNAUTHORIZED))


def create_user(request: Request) -> Response:
    """ The first step to creating a user.
    If successful, this ends with an email being
    sent to the provided email which contains
    a verification link.

    We don't ask for the password yet, they need to get past
    email verification first

    No state is changed here
    """
    req_body = request.get_json()
    email = req_body['email']
    db_session = create_session()

    # check if user exists already
    existing_user = db_session.query(
        models.User).filter(
        models.User.email == email).first()
    if existing_user is not None:
        return current_app.make_response((f'user with email {email} already exists',
                                         HTTPStatus.BAD_REQUEST))

    # send them the email with the jwt
    jwt = utils.create_jwt(
        email=email,
        timediff=current_app.config['JWT_EMAIL_VERIFICATION_EXPIRY'])

    if utils.get_flask_env() == utils.FlaskEnv.PRODUCTION:
        emailer.send_email("Bloomint verification email",
                           f"Click this link to verify your \
                           email address: {utils.get_base_address()}/static/authorize?jwt={jwt}",
                           email)
        return current_app.make_response(
            ({'success'}, HTTPStatus.OK))
    else:
        # When we run the test, it's too painful to set up the email stuff.
        # Just return the jwt in the response so they confirm their email
        # address and set their password
        return current_app.make_response(
            ({'jwt': jwt}, HTTPStatus.OK))


def verify_user(request: Request) -> Response:
    """ Confirm the users email is legit,
    grab their password here,
    and finally add the new user into the database.
    """
    req_body = request.get_json()
    password = req_body['password']
    email = utils.try_get_user_email(request)

    min_password_length = current_app.config['MIN_PASSWORD_LENGTH']
    max_password_length = current_app.config['MAX_PASSWORD_LENGTH']
    if len(password) < min_password_length or len(
            password) > max_password_length:
        return current_app.make_response((f'Password length must be between {min_password_length} and {max_password_length}',
                                         HTTPStatus.BAD_REQUEST))

    db_session = create_session()

    # check if user exists already
    # we check again here. It's unlikely
    # but possible that someone took the email between
    # the time we sent the verification email, and the time
    # they actually click it and end up here.
    # yes there is also a race condition here for a similar reason
    existing_user = db_session.query(
        models.User).filter(
        models.User.email == email).first()
    if existing_user is not None:
        return current_app.make_response((f'user with email {email} already exists',
                                         HTTPStatus.BAD_REQUEST))

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

    return current_app.make_response(
        ('Successfully registered user with password', HTTPStatus.OK))


def delete_user(request: Request) -> Response:
    req_body = request.get_json()
    password = req_body['password']
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

    return current_app.make_response(
        ('Success', HTTPStatus.OK))


def get_user(request: Request) -> Response:
    email = utils.try_get_user_email(request)

    db_session = create_session()
    user = db_session.query(models.User).filter(
        models.User.email == email).first()

    return current_app.make_response(
        ({
            'email': user.email,
            'created_at': user.created_at
        }, HTTPStatus.OK))
