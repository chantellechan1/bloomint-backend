from flask import Blueprint, request, current_app, jsonify
import datetime
from http import HTTPStatus

from .. import utils
from .. import create_session
from . import models as plant_models
from ..auth import models as auth_models

plant_blueprint = Blueprint('plant', __name__)


# local utils


def get_user_id_from_email(db_session, email) -> int:
    user = db_session.query(
        auth_models.User).filter(
        auth_models.User.email == email,
        auth_models.User.deleted_at == None).first()  # noqa
    user_id = user.id
    return user_id


def format_plant(plant_row):
    formatted_plant = {
        'id': plant_row.id,
        'user_id': plant_row.user_id,
        'plant_id': plant_row.plant_id,
        'plant_name': plant_row.plant_name,
        'notes': plant_row.notes,
        'purchased_at': plant_row.purchased_at,
        'created_at': plant_row.created_at
    }
    return formatted_plant


# route returns list of user_plant_ids (ids of unique plants that the user
# owns)
@plant_blueprint.route('/plants/user/get_plant_ids', methods=['GET'])
def getUserPlantIds():
    try:

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        # get plant_ids from user_ids
        result = db_session.query(
            plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id,
            plant_models.UsersPlants.deleted_at == None)  # noqa
        plant_ids = map(lambda row: row.id, result)
        plant_ids = list(plant_ids)

        res = current_app.make_response(
            (jsonify(plant_ids), HTTPStatus.OK))

    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
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

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        # get plants from user_id and plant_ids
        result = db_session.query(plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id,
            plant_models.UsersPlants.id.in_(plant_ids),
            plant_models.UsersPlants.deleted_at == None  # noqa
        )

        plants = map(format_plant, result)
        plants = list(plants)

        res = current_app.make_response(
            (jsonify(plants), HTTPStatus.OK))

    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res


# this route returns all the types of plants that a user owns, as well as
# the number of each type of plant they own


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
        user_id = get_user_id_from_email(db_session, email)

        # get plant_ids from user_ids
        result = db_session.query(plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id, plant_models.UsersPlants.deleted_at == None)  # noqa
        plant_ids = map(lambda plant: plant.plant_id, result)
        plant_ids = list(plant_ids)

        # get plants from plant_ids
        # the <Column>.in_() functions expects a list of acceptable plant ids
        userPlants = db_session.query(plant_models.Plant).filter(
            plant_models.Plant.id.in_(plant_ids),
            plant_models.Plant.deleted_at == None  # noqa
        )

        # format to return to user
        formattedUserPlants = []

        for plant in userPlants:
            # plant.id on following line is id on Plants table (plant type id)
            num_plants_owned = plant_ids.count(plant.id)

            formattedUserPlants.append({
                'id': plant.id,
                'name': plant.name,
                'num_owned': num_plants_owned,
                'sunlight': plant.sunlight,
                'min_temp': plant.min_temp,
                'max_temp': plant.max_temp,
                'water_frequency': plant.water_frequency,
                'created_at': plant.created_at
            })

        res = current_app.make_response(
            (jsonify(formattedUserPlants), HTTPStatus.OK))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res


# route returns list of specific plants owned by a user
# POST request body should contain array of plant_ids
@plant_blueprint.route('/plants/user/plants_by_type', methods=['POST'])
def getPlantsByType():
    try:
        # get list of plant ids from request body
        req_body = request.get_json()
        plant_type_id = req_body['plant_type_id']
        print(f"plant_type_id: {plant_type_id}")

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        # get plants from user_id and plant_ids
        result = db_session.query(plant_models.UsersPlants).filter(
            plant_models.UsersPlants.user_id == user_id,
            plant_models.UsersPlants.plant_id == plant_type_id,
            plant_models.UsersPlants.deleted_at == None  # noqa
        )

        plants = map(format_plant, result)
        plants = list(plants)

        res = current_app.make_response(
            (jsonify(plants), HTTPStatus.OK))

    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))
    return res


# route to create individual plants


@plant_blueprint.route('/plants/user/create', methods=['POST'])
def createPlants():
    try:
        req_body = request.get_json()

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        def make_plant(plant_row):
            new_plant = plant_models.UsersPlants(
                user_id=user_id,
                plant_id=plant_row['plant_id'],
                created_at=datetime.datetime.utcnow()
            )

            if 'plant_name' in plant_row:
                new_plant.plant_name = plant_row['plant_name']

            if 'notes' in plant_row:
                new_plant.notes = plant_row['notes']

            if 'purchased_at' in plant_row:
                new_plant.purchased_at = plant_row['purchased_at']

            return new_plant

        new_plant_list = map(make_plant, req_body)
        new_plant_list = list(new_plant_list)

        db_session.add_all(new_plant_list)

        db_session.commit()

        res = current_app.make_response(
            ('success', HTTPStatus.OK))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))

    return res


# route to delete plants
# post body expects arrays of userplant_ids


@plant_blueprint.route('/plants/user/delete', methods=['POST'])
def deletePlants():
    try:
        req_body = request.get_json()
        userPlantIDs = req_body['user_plant_ids']

        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        # update deleted_at column in UsersPlants table
        db_session.query(
            plant_models.UsersPlants
        ).filter(
            plant_models.UsersPlants.user_id == user_id,
            plant_models.UsersPlants.id.in_(userPlantIDs),
            plant_models.UsersPlants.deleted_at == None  # noqa
        ).update(
            {plant_models.UsersPlants.deleted_at: datetime.datetime.utcnow()},
            synchronize_session=False
        )

        # commit changes
        db_session.commit()

        res = current_app.make_response(
            ('success', HTTPStatus.BAD_REQUEST))
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))

    return res


# route to delete plants
# post body expects arrays of userplant_ids
@plant_blueprint.route('/plants/user/update', methods=['POST'])
def updatePlants():
    try:
        plants_to_update = request.get_json()
        db_session = create_session()

        # get email from jwt in auth header
        email = utils.try_get_user_email(request)

        # get user_id from email
        user_id = get_user_id_from_email(db_session, email)

        for updated_plant in plants_to_update:
            # get plant to update from db
            db_plant = db_session.query(
                plant_models.UsersPlants
            ).filter(
                plant_models.UsersPlants.user_id == user_id,
                plant_models.UsersPlants.id == updated_plant['id'],
                plant_models.UsersPlants.deleted_at == None  # noqa
            ).first()

            # update plant properties
            db_plant.plant_id = updated_plant['plant_id']
            db_plant.plant_name = updated_plant['plant_name']
            db_plant.notes = updated_plant['notes']
            db_plant.purchased_at = updated_plant['purchased_at']

            # commit changes
            db_session.commit()

        res = current_app.make_response(
            ('success', HTTPStatus.OK)
        )
    except BaseException:
        res = current_app.make_response(
            ('Something Bad Happened', HTTPStatus.BAD_REQUEST))

    return res
