from flask import Blueprint, request
from . import auth
from .. import utils

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    return utils.handle_api_request(auth.login, request)


@auth_blueprint.route('/auth/create_user', methods=['POST'])
def create_user():
    return utils.handle_api_request(auth.create_user, request)


@auth_blueprint.route('/auth/verify_user', methods=['POST'])
def verify_user():
    return utils.handle_api_request(auth.verify_user, request)


@auth_blueprint.route('/auth/delete_user', methods=['POST'])
def delete_user():
    return utils.handle_api_request(auth.delete_user, request)


@auth_blueprint.route('/auth/get_user', methods=['GET'])
def get_user():
    return utils.handle_api_request(auth.get_user, request)
