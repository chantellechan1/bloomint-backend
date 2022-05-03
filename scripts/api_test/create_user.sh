if ! [[ $1 ]]
then
    echo "usage: ./scripts/api_test/create_user.sh <dummy username>"
    exit
fi

EMAIL=$1
PASSWORD=hector_hector_hector
URL=http://127.0.0.1:5000

################# Signup ##################
SIGNUP_RESPONSE=$(curl \
    --header "Content-Type: application/json" \
    --data '{"email":"'$EMAIL'"}' \
    --silent \
    $URL/auth/create_user)
echo $SIGNUP_RESPONSE
SIGNUP_JWT=$(echo $SIGNUP_RESPONSE | jq .jwt)

VERIFY_USER_RESPONSE=$(curl \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $SIGNUP_JWT" \
    --data '{"password":"'$PASSWORD'"}' \
    --silent \
    $URL/auth/verify_user)

################# Login ##################
LOGIN_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'", "email":"'$EMAIL'"}' \
    --silent \
    $URL/auth/login)

JWT=$(echo $LOGIN_RESPONSE | jq .jwt)

echo "Logged in with jwt: $JWT"

GET_USER_RESPONSE=$(curl \
    --request GET \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $SIGNUP_JWT" \
    --silent \
    $URL/auth/get_user)

echo "info about myself: $GET_USER_RESPONSE"
