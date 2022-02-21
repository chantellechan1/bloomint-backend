from flask import Blueprint, render_template, request
from .. import utils

static_blueprint = Blueprint('static', __name__)


@static_blueprint.route('/static/authorize', methods=['GET'])
def authorize():
    try:
        jwt = request.args['jwt']
        baseUrl = utils.get_base_address()
        return render_template('authorize.html',
                               jwt=jwt,
                               baseUrl=baseUrl)
    except BaseException:
        return render_template('error.html')
