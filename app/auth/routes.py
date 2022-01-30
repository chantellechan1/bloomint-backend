from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from .. import create_session
from . import models

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    req_body = request.get_json()
    email = req_body['email']
    password = req_body['password']
    try:
        db_session = create_session()
        result = db_session.query(models.User).filter(models.User.email==email).first()
        stored_hash = result.hashed_password
        res = current_app.make_response(({'user_hash': stored_hash}, current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
        
        if check_password_hash(stored_hash, password + current_app.config['PEPPER']):
            current_datetime = datetime.datetime.utcnow()
            expiry_datetime = current_datetime + current_app.config['JWT_TIME_DIFF']
            payload = {
                'email': email,
                'exp': str(expiry_datetime)
            }
            encoded_jwt = jwt.encode(
                payload, current_app.config['JWT_SECRET'], algorithm=current_app.config['JWT_ALG'])
            res = current_app.make_response(({'token': encoded_jwt}, current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
        else:
            res = current_app.make_response(('Login Failed', current_app.config['HTTP_STATUS_CODES']['UNAUTHORIZED']))
    except:
        res = current_app.make_response(('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res

@auth_blueprint.route('/auth/create_user', methods=['POST'])
def create_user():
    req_body = request.get_json()
    email = req_body['email']
    password = req_body['password']

    try:
        db_session = create_session()

        # TODO: check if user exists already
        # result = db_session.query(User).filter(User.email==email).first()

        # TODO: check password min/max length

        # create hashed password
        hashed_password = generate_password_hash(password + current_app.config['PEPPER'], salt_length=128)

        # make creation date
        create_date = datetime.datetime.utcnow()

        # create user object
        user = models.User(email=email, hashed_password=hashed_password, created_at=create_date)

        # add user to table
        db_session.add(user)

        # commit transaction
        db_session.commit()

        res = current_app.make_response(('Success', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    except:
        res = current_app.make_response(('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['BAD_REQUEST']))

    return res
