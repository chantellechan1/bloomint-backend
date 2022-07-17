from flask import Blueprint, request
from . import plant
from .. import utils

plant_blueprint = Blueprint('plant', __name__)


# route returns list of user_plant_ids (ids of unique plants that the user
# owns)
@plant_blueprint.route('/plants/user/get_plant_ids', methods=['GET'])
def getUserPlantIds():
    return utils.handle_api_request(plant.getUserPlantIds, request)


# route returns list of specific plants owned by a user
# POST request body should contain array of plant_ids
@plant_blueprint.route('/plants/user/get_plants', methods=['POST'])
def getUserPlants():
    return utils.handle_api_request(plant.getUserPlants, request)


# this route returns plant type information
# provided that an array of plant type IDs are supplied in the body
@plant_blueprint.route('/plants/plant_types', methods=['POST'])
def findPlantTypes():
    return utils.handle_api_request(plant.findPlantTypes, request)


# this route returns all the types of plants that a user owns, as well as
# the number of each type of plant they own
@plant_blueprint.route('/plants/user/plant_types', methods=['GET'])
def allPlantTypesOwnedByUser():
    return utils.handle_api_request(plant.allPlantTypesOwnedByUser, request)


# return all plant types (regardless of whether a user owns a plant of
# this type)
@plant_blueprint.route('/plants/plant_types/all', methods=['GET'])
def plantTypesAll():
    return utils.handle_api_request(plant.plantTypesAll, request)


# route returns list of specific plants owned by a user
# POST request body should contain array of plant_ids
@plant_blueprint.route('/plants/user/plants_by_type', methods=['POST'])
def getPlantsByType():
    return utils.handle_api_request(plant.getPlantsByType, request)


# route to create individual plants
@plant_blueprint.route('/plants/user/create', methods=['POST'])
def createUserPlants():
    return utils.handle_api_request(plant.createUserPlants, request)


# route to delete plants
# post body expects arrays of userplant_ids
@plant_blueprint.route('/plants/user/delete', methods=['POST'])
def deletePlants():
    return utils.handle_api_request(plant.deletePlants, request)


# route to update plants
@plant_blueprint.route('/plants/user/update', methods=['POST'])
def updatePlants():
    return utils.handle_api_request(plant.updatePlants, request)


# route to create images
@plant_blueprint.route('/plants/images/create', methods=['POST'])
def createUserPlantImage():
    return utils.handle_api_request(plant.createUserPlantImage, request)


@plant_blueprint.route('/plants/images/getByUserPlantIds', methods=['POST'])
def getImagesGivenUserPlantIds():
    return utils.handle_api_request(plant.getImagesGivenUserPlantIds, request)


@plant_blueprint.route('/plants/images/delete', methods=['POST'])
def deleteImagesGivenUserPlantImageIds():
    return utils.handle_api_request(
        plant.deleteImagesGivenUserPlantImageIds, request)
