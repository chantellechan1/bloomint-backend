if ! [[ $1 ]]
then
    echo "usage: ./scripts/apit_test/plants.sh <dummy username>"
    exit
fi

EMAIL=$1
PASSWORD=hector_hector_hector
URL=http:/127.0.0.1:5000

################# Login ##################
LOGIN_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'", "email":"'$EMAIL'"}' \
    --silent \
    $URL/auth/login)
JWT=$(echo $LOGIN_RESPONSE | jq .jwt)
if [ $? -ne 0 ]; then
    echo "Failed to log in as $EMAIL"
    echo "Did you remember to run create user first?"
    exit
fi

################# Test Plants API  ##################

# Get all the different types of plants that exist
# and just use a random one from the list
# to create a user plant
GET_ALL_PLANTTYPES_RESPONSE=$(curl \
    --request GET \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --silent \
    $URL/plants/plant_types/all)

PLANT_TYPE_ID=$(echo $GET_ALL_PLANTTYPES_RESPONSE | jq .[0].id)

# Find some info about this plant type.
GET_PLANTTYPE_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data "{\"plant_type_ids\": [$PLANT_TYPE_ID]}" \
    --silent \
    $URL/plants/plant_types)
echo "Get plant type response: $GET_PLANTTYPE_RESPONSE"

# Create the user plant
CREATE_USER_PLANT_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data '[{"plant_id":"'$PLANT_TYPE_ID'", "plant_name":"the_test_plant", "notes":"This plant was created a as test"}]' \
    --silent \
    $URL/plants/user/create)

# Get the ID of user plant(s)
GET_USER_PLANT_IDS_RESPONSE=$(curl \
    --request GET \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --silent \
    $URL/plants/user/get_plant_ids)

USER_PLANT_ID=$(echo $GET_USER_PLANT_IDS_RESPONSE | jq .[0])

# Get info about that plant.
# There is no guarantee it's the same one we created above
GET_USER_PLANTS_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data "{\"plant_ids\": [$USER_PLANT_ID]}" \
    --silent \
    $URL/plants/user/get_plants)
echo "info about one of the users plants: $GET_USER_PLANTS_RESPONSE"

# Get info about all the plant types that the user owns
GET_USER_PLANT_TYPES_RESPONSE=$(curl \
    --request GET \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --silent \
    $URL/plants/user/plant_types)
echo "info about the plant types that user owns: $GET_USER_PLANT_TYPES_RESPONSE"

GET_USER_PLANTS_BY_TYPE_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data "{\"plant_type_id\": $PLANT_TYPE_ID}" \
    --silent \
    $URL/plants/user/plants_by_type)
NUM_PLANTS_BY_TYPE=$(echo $GET_USER_PLANTS_BY_TYPE_RESPONSE | jq length)
echo "get plants by type had: $NUM_PLANTS_BY_TYPE plants"

UPDATE_USER_PLANTS_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data '[{"id":"'$USER_PLANT_ID'", "plant_name":"the_test_plant UPDATED", "notes":"UPDATED This plant was created a as test"}]' \
    --silent \
    $URL/plants/user/update)

GET_USER_PLANTS_AFTER_UPDATE_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data "{\"plant_ids\": [$USER_PLANT_ID]}" \
    --silent \
    $URL/plants/user/get_plants)
echo "info about one of the users plants after update: $GET_USER_PLANTS_AFTER_UPDATE_RESPONSE"

# delete a user plant
DELETE_USER_PLANT=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data "{\"user_plant_ids\": [$USER_PLANT_ID]}" \
    --silent \
    $URL/plants/user/delete)

GET_USER_PLANT_IDS_AFTER_DELETE_RESPONSE=$(curl \
    --request GET \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --silent \
    $URL/plants/user/get_plant_ids)
echo "After delete, get user plant ids: $GET_USER_PLANT_IDS_AFTER_DELETE_RESPONSE"
