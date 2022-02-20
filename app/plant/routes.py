from crypt import methods
from flask import Blueprint, request, current_app, jsonify
import datetime
import jwt
import pdb

from .. import utils
from .. import create_session
from . import models as plant_models
from ..auth import models as auth_models

plant_blueprint = Blueprint('plant', __name__)

# route returns list of user_plant_ids (ids of unique plants that the user owns)
@plant_blueprint.route('/plants/user/get_plant_ids', methods=['GET'])
def getUserPlantIds():
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
        plant_ids = map(lambda row: row.id, result)
        plant_ids = list(plant_ids)

        res = current_app.make_response((jsonify(plant_ids), current_app.config['HTTP_STATUS_CODES']['SUCCESS']))

    except:
        res = current_app.make_response(('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res

# route returns list of specific plants owned by a user
# POST request body should contain array of plant_ids
@plant_blueprint.route('/plants/user/get_plants', methods=['POST'])
def getUserPlants():
    try:
        # get list of plant ids from request body
        req_body = request.get_json()
        plant_ids = req_body['plant_ids']
        print('plant_ids:')
        print(' '.join([str(elem) for elem in plant_ids]))

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # pdb.set_trace()


        # get user_id from email
        user = db_session.query(auth_models.User).filter(auth_models.User.email==email, auth_models.User.deleted_at == None).first()
        user_id = user.id
        print(f'user id is {user_id}')

        # get plants from user_id and plant_ids
        result = db_session.query(plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id, 
            plant_models.UsersPlants.id.in_(plant_ids), 
            plant_models.UsersPlants.deleted_at == None
        )

        def format_plant(plant_row): 
            formatted_plant = {
                'id': plant_row.id, 
                'user_id': plant_row.user_id, 
                'plant_type_id': plant_row.plant_id, 
                'plant_name': plant_row.plant_name,
                'notes': plant_row.notes,
                'purchased_at': plant_row.purchased_at,
                'created_at': plant_row.created_at
            }
            return formatted_plant
       
        plants = map(format_plant, result)
        plants = list(plants)

        res = current_app.make_response((jsonify(plants), current_app.config['HTTP_STATUS_CODES']['SUCCESS']))

    except:
        res = current_app.make_response(('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res
    
# this route returns all the types of plants that a user owns, as well as the number of each type of plant they own
@plant_blueprint.route('/plants/user/plant_types', methods=['GET'])
def allUserPlants():

    # TODO: implement pagination so only 10 plant types are returned at once
    # 10 was picked as a reasonable number of plant types to look at on one
    # page
    try:

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user = db_session.query(auth_models.User).filter(
            auth_models.User.email == email, auth_models.User.deleted_at is None).first()
        user_id = user.id
        print(f'user id is {user_id}')

        # get plant_ids from user_ids
        result = db_session.query(plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id, plant_models.UsersPlants.deleted_at is None)
        plant_ids = map(lambda plant: plant.plant_id, result)
        plant_ids = list(plant_ids)

        # get plants from plant_ids
        # the <Column>.in_() functions expects a list of acceptable plant ids
        userPlants = db_session.query(plant_models.Plant).filter(
            plant_models.Plant.id.in_(plant_ids), plant_models.Plant.deleted_at is None)

        # TODO: return count of how many of each type of plant a user owns

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

        res = current_app.make_response(
            (jsonify(formattedUserPlants), current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', current_app.config['HTTP_STATUS_CODES']['SUCCESS']))
    return res