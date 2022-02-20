if ! [[ $1 ]]
then
    echo "usage: ./scripts/api_test/delete_user.sh <dummy username>"
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
    $URL/auth/login)
JWT=$(echo $LOGIN_RESPONSE | jq .jwt)
if [ $? -ne 0 ]; then
    echo "Failed to log in as $EMAIL"
    echo "Did you remember to run create user first?"
    exit
fi

################# DELETE USER ##################
DELETE_USER_RESPONSE=$(curl \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'"}' \
    $URL/auth/delete_user)
