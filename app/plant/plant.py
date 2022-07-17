from flask import current_app, jsonify
from flask.wrappers import Request, Response
import datetime
from http import HTTPStatus
import base64

from .. import utils
from .. import create_session
from . import models as plant_models


# local utils
def format_plant(plant_row):
    formatted_plant = {
        'id': plant_row.id,
        'user_id': plant_row.user_id,
        'plant_id': plant_row.planttype_id,
        'plant_name': plant_row.plant_name,
        'notes': plant_row.notes,
        'purchased_at': plant_row.purchased_at,
        'created_at': plant_row.created_at
    }
    return formatted_plant
# TODO: return info about a plant type - POST body should have plant_type_id


def getUserPlantIds(request: Request) -> Response:
    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plant_ids from user_ids
    result = db_session.query(
        plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id,
        plant_models.UserPlant.deleted_at == None)  # noqa
    plant_ids = map(lambda row: row.id, result)
    plant_ids = list(plant_ids)

    return current_app.make_response(
        (jsonify(plant_ids), HTTPStatus.OK))


def getUserPlants(request: Request) -> Response:
    # get list of plant ids from request body
    req_body = request.get_json()
    plant_ids = req_body['plant_ids']
    print('plant_ids:')
    print(' '.join([str(elem) for elem in plant_ids]))

    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plants from user_id and plant_ids
    result = db_session.query(plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id,
        plant_models.UserPlant.id.in_(plant_ids),
        plant_models.UserPlant.deleted_at == None  # noqa
    )

    plants = map(format_plant, result)
    plants = list(plants)

    return current_app.make_response(
        (jsonify(plants), HTTPStatus.OK))


def findPlantTypes(request: Request) -> Response:
    # get list of plant ids from request body
    req_body = request.get_json()
    plant_type_ids = req_body['plant_type_ids']
    print('plant_type_ids:')
    print(' '.join([str(elem) for elem in plant_type_ids]))

    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plants from plant_ids
    # the <Column>.in_() functions expects a list of acceptable plant ids
    plantTypes = db_session.query(plant_models.PlantType).filter(
        plant_models.PlantType.id.in_(plant_type_ids),
        plant_models.PlantType.deleted_at == None  # noqa
    )

    # get plant_ids from user_ids
    result = db_session.query(plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id, plant_models.UserPlant.deleted_at == None)  # noqa
    plant_ids = map(lambda plant: plant.planttype_id, result)
    plant_ids = list(plant_ids)

    # format to return to user
    formattedPlants = []

    for plant in plantTypes:
        num_plants_owned = plant_ids.count(plant.id)

        formattedPlants.append({
            'id': plant.id,
            'name': plant.name,
            'num_owned': num_plants_owned,
            'sunlight': plant.sunlight,
            'min_temp': plant.min_temp,
            'max_temp': plant.max_temp,
            'water_frequency': plant.water_frequency,
            'created_at': plant.created_at
        })

    return current_app.make_response(
        (jsonify(formattedPlants), HTTPStatus.OK))


def allPlantTypesOwnedByUser(request: Request) -> Response:
    # TODO: implement pagination so only 10 plant types are returned at once
    # 10 was picked as a reasonable number of plant types to look at on one
    # page
    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plant_ids from user_ids
    result = db_session.query(plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id, plant_models.UserPlant.deleted_at == None)  # noqa
    plant_ids = map(lambda plant: plant.planttype_id, result)
    plant_ids = list(plant_ids)

    # get plants from plant_ids
    # the <Column>.in_() functions expects a list of acceptable plant ids
    userPlants = db_session.query(plant_models.PlantType).filter(
        plant_models.PlantType.id.in_(plant_ids),
        plant_models.PlantType.deleted_at == None  # noqa
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

    return current_app.make_response(
        (jsonify(formattedUserPlants), HTTPStatus.OK))


def plantTypesAll(request: Request) -> Response:
    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plant_ids from user_ids (UserPlantIDs)
    result = db_session.query(plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id, plant_models.UserPlant.deleted_at == None)  # noqa
    plant_ids = map(lambda plant: plant.planttype_id, result)
    plant_ids = list(plant_ids)

    # get plants from plant_ids
    # the <Column>.in_() functions expects a list of acceptable plant ids
    userPlants = db_session.query(plant_models.PlantType).filter(
        plant_models.PlantType.deleted_at == None  # noqa
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

    return current_app.make_response(
        (jsonify(formattedUserPlants), HTTPStatus.OK))


def getPlantsByType(request: Request) -> Response:
    # get list of plant ids from request body
    req_body = request.get_json()
    plant_type_id = req_body['plant_type_id']
    print(f"plant_type_id: {plant_type_id}")

    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # get plants from user_id and plant_ids
    result = db_session.query(plant_models.UserPlant).filter(
        plant_models.UserPlant.user_id == user_id,
        plant_models.UserPlant.planttype_id == plant_type_id,
        plant_models.UserPlant.deleted_at == None  # noqa
    )

    plants = map(format_plant, result)
    plants = list(plants)

    return current_app.make_response(
        (jsonify(plants), HTTPStatus.OK))


def createUserPlants(request: Request) -> Response:
    req_body = request.get_json()

    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    def make_plant(plant_row):
        new_plant = plant_models.UserPlant(
            user_id=user_id,
            planttype_id=plant_row['plant_id'],
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

    new_plant_ids = list(
        map(lambda userPlant: userPlant.id, list(new_plant_list)))

    return current_app.make_response(
        ({'status': 'success', 'data': new_plant_ids}, HTTPStatus.OK))


def deletePlants(request: Request) -> Response:
    req_body = request.get_json()
    userPlantIDs = req_body['user_plant_ids']

    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # update deleted_at column in UserPlants table
    db_session.query(
        plant_models.UserPlant
    ).filter(
        plant_models.UserPlant.user_id == user_id,
        plant_models.UserPlant.id.in_(userPlantIDs),
        plant_models.UserPlant.deleted_at == None  # noqa
    ).update(
        {plant_models.UserPlant.deleted_at: datetime.datetime.utcnow()},
        synchronize_session=False
    )

    # commit changes
    db_session.commit()

    return current_app.make_response(
        ('success', HTTPStatus.OK))


def updatePlants(request: Request) -> Response:
    plants_to_update = request.get_json()
    db_session = create_session()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    for updated_plant in plants_to_update:
        # get plant to update from db
        db_plant = db_session.query(
            plant_models.UserPlant
        ).filter(
            plant_models.UserPlant.user_id == user_id,
            plant_models.UserPlant.id == updated_plant['id'],
            plant_models.UserPlant.deleted_at == None  # noqa
        ).first()

        # update plant properties
        if 'plant_id' in updated_plant:
            db_plant.plant_id = updated_plant['plant_id']
        if 'plant_name' in updated_plant:
            db_plant.plant_name = updated_plant['plant_name']
        if 'notes' in updated_plant:
            db_plant.notes = updated_plant['notes']
        if 'purchased_at' in updated_plant:
            db_plant.purchased_at = updated_plant['purchased_at']

        # commit changes
        db_session.commit()

    return current_app.make_response(
        ('success', HTTPStatus.OK))


def createUserPlantImage(request: Request) -> Response:
    images = request.get_json()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)

    db_session = create_session()
    # get user_id from email
    user_id = utils.get_user_id_from_email(db_session, email)

    # check that user plant user id matches the user id
    for image in images:
        user_plant_id = image['user_plant_id']
        user_plant = db_session.query(plant_models.UserPlant).filter(
                plant_models.UserPlant.id == user_plant_id,
                plant_models.UserPlant.deleted_at == None).first()  # noqa

        if user_plant is None:
            return current_app.make_response(
                (f'could not find user plant with id {user_plant_id}', HTTPStatus.BAD_REQUEST))
        if user_plant.user_id != user_id:
            return current_app.make_response(
                ('plant does not belong to you', HTTPStatus.BAD_REQUEST))

    new_images_list = []
    # create new Image and UserPlantImage objects and append to
    # new_items_list
    # use index to guarantee same ordering in both loops
    for i in range(len(images)):
        image = images[i]
        image_binary = base64.b64decode(image['image_base_64'])
        new_image = plant_models.Image(
            image=image_binary,
            created_at=datetime.datetime.utcnow()
        )

        new_images_list.append(new_image)

    # Hopefully this will generate the IDs
    # which we use to link user plant image to
    # the image
    db_session.add_all(new_images_list)
    db_session.commit()

    # use index to guarantee same ordering in both loops
    new_user_plant_images = []
    for i in range(len(new_images_list)):
        new_image = new_images_list[i]
        image = images[i]
        new_user_plant_image = plant_models.UserPlantImage(
            image_id=new_image.id,
            user_plant_id=image['user_plant_id'],
            created_at=datetime.datetime.utcnow()
        )
        new_user_plant_images.append(new_user_plant_image)

    db_session.add_all(new_user_plant_images)
    db_session.commit()

    return current_app.make_response(
        ('success', HTTPStatus.OK))


def getImagesGivenUserPlantIds(request: Request) -> Response:
    user_plant_ids = request.get_json()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)
    db_session = create_session()

    user_id = utils.get_user_id_from_email(db_session, email)

    images_list = []
    for user_plant_id in user_plant_ids:
        user_plant = db_session.query(plant_models.UserPlant).filter(
            plant_models.UserPlant.id == user_plant_id,
            plant_models.UserPlant.deleted_at == None).first()  # noqa

        if user_plant.user_id != user_id:
            return current_app.make_response(
                ('plant does not belong to you', HTTPStatus.BAD_REQUEST))

        user_plant_images = db_session.query(plant_models.UserPlantImage).filter(
                plant_models.UserPlantImage.user_plant_id == user_plant_id,
                plant_models.UserPlantImage.deleted_at == None)  # noqa
        for user_plant_image in user_plant_images:
            image = db_session.query(plant_models.Image).filter(
                    plant_models.Image.id == user_plant_image.image_id,
                    plant_models.Image.deleted_at == None).first()  # noqa
            encoded_image = base64.b64encode(image.image)
            encoded_image_str = str(encoded_image, "utf-8")
            json_image = {
                "image_id": image.id,
                "user_plant_id": user_plant_id,
                "image_data": encoded_image_str}
            images_list.append(json_image)

    return current_app.make_response(
        (jsonify(images_list), HTTPStatus.OK))


def deleteImagesGivenUserPlantImageIds(request: Request) -> Response:
    image_ids = request.get_json()

    # get email from jwt in auth header
    email = utils.try_get_user_email(request)
    db_session = create_session()

    user_id = utils.get_user_id_from_email(db_session, email)

    for image_id in image_ids:
        user_plant_image = db_session.query(plant_models.UserPlantImages).filter(
            plant_models.UserPlantImages.image_id == image_id,
            plant_models.UserPlantImages.deleted_at == None).first()  # noqa

        user_plant = db_session.query(plant_models.UserPlant).filter(
                plant_models.UserPlant.id == user_plant_image.user_plant_id,
                plant_models.UserPlantImages.deleted_at == None).first()  # noqa

        if user_plant.user_id != user_id:
            return current_app.make_response(
                ('plant does not belong to you', HTTPStatus.BAD_REQUEST))

        db_session.query(plant_models.Images).filter(
                    plant_models.Images.id == image_id,
                    plant_models.Images.deleted_at == None).update(  # noqa
                    {plant_models.Images.deleted_at: datetime.datetime.utcnow()},
                    synchronize_session=False)

        db_session.query(plant_models.UserPlantImages).filter(
                plant_models.UserPlantImages.image_id == image_id,
                plant_models.UserPlantImages.deleted_at == None).update(  # noqa
                    {plant_models.Images.deleted_at: datetime.datetime.utcnow()},
                    synchronize_session=False)

    current_app.make_response(
        ('Success', HTTPStatus.OK))
