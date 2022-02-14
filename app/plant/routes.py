from flask import Blueprint, request, current_app, jsonify
import datetime
import jwt

from .. import utils
from .. import create_session
from . import models as plant_models
from ..auth import models as auth_models

plant_blueprint = Blueprint('plant', __name__)

# this function returns all the types of plants that a user owns, as well as the number of each type of plant they own
@plant_blueprint.route('/plants/user/plant_types', methods=['GET'])
def allUserPlants():

    # TODO: implement pagination so only 10 plant types are returned at once
    # 10 was picked as a reasonable number of plant types to look at on one page
    try:

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user = db_session.query(auth_models.User).filter(auth_models.User.email==email, auth_models.User.deleted_at == None).first()
        user_id = user.id
        print(f'user id is {user_id}')

        # get plant_ids from user_ids
        result = db_session.query(plant_models.UsersPlants).filter(plant_models.UsersPlants.user_id == user_id, plant_models.UsersPlants.deleted_at == None)
        plant_ids = map(lambda plant: plant.plant_id, result)
        plant_ids = list(plant_ids)

        # get plants from plant_ids
        # the <Column>.in_() functions expects a list of acceptable plant ids
        userPlants = db_session.query(plant_models.Plant).filter(plant_models.Plant.id.in_(plant_ids), plant_models.Plant.deleted_at == None)

        # format to return to user
        formattedUserPlants = []

        for plant in userPlants:
            num_plants_owned = plant_ids.count(plant.id)

            formattedUserPlants.append({
                'id': plant.id,
                'name': plant.name,
                'sunlight': plant.sunlight,
                'min_temp': plant.min_temp,
                'max_temp': plant.max_temp,
                'water_frequency': plant.water_frequency,
                'created_at': plant.created_at,
                'num_owned': num_plants_owned
            })
            
        res = current_app.make_response((jsonify(formattedUserPlants), current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    except:
        res = current_app.make_response(('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res

