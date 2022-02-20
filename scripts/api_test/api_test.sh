if ! [[ $1 ]]
then
    echo "usage: ./scripts/api_test.sh <dummy username>"
    echo "Im still trying to figure out how to reset the database at the start of the script, "
    echo "so for now you need to pass in a different username each time"
    exit
fi

EMAIL=$1
PASSWORD=hector_hector_hector
URL=localhost:5000

# Change to test mode first.
# This changest the behaviour of the
# server a bit, just to make testing easier
# (or else we need to do things like
# set up an email server)
SCRIPTS_FOLDER=$(dirname $(realpath "$0"))
source "$SCRIPTS_FOLDER/../set_test.sh"

################# Signup ##################
SIGNUP_RESPONSE=$(curl \
    --header "Content-Type: application/json" \
    --data '{"email":"'$EMAIL'"}' \
    $URL/auth/create_user)

SIGNUP_JWT=$(echo $SIGNUP_RESPONSE | jq .jwt)

VERIFY_USER_RESPONSE=$(curl \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $SIGNUP_JWT" \
    --data '{"password":"'$PASSWORD'"}' \
    $URL/auth/verify_user)

################# Login ##################
LOGIN_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'", "email":"'$EMAIL'"}' \
    $URL/auth/login)
JWT=$(echo $LOGIN_RESPONSE | jq .token)

################# Plants API ##################

GET_PLANTTYPES_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    $URL/plants/plant_types/all)

#CREATE_USER_PLANT_IDS_RESPONSE=$(curl \
#    --request POST \
#    --header "Content-Type: application/json" \
#    --header "Authorization: Bearer $JWT" \
#    --header "accept: application/json" \
#    --data "" \
#    $URL/plants/user/create)
#
#GET_USER_PLANT_IDS_RESPONSE=$(curl \
#    --request GET \
#    --header "Content-Type: application/json" \
#    --header "Authorization: Bearer $JWT" \
#    --header "accept: application/json" \
#    $URL/plants/user/get_plant_ids)
#
#PLANT_IDS=$(echo $GET_USER_PLANT_IDS_RESPONSE | jq .)

################# DELETE USER ##################
DELETE_USER_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'"}' \
    $URL/auth/delete_user)
