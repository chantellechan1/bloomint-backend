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


# create user
curl --header "Content-Type: application/json" -d '{"email":"'$EMAIL'"}' $URL/auth/create_user

# login and retrieve jwt
CURL_LOGIN=$(curl \
    --silent \
    --request POST \
    --header "Content-Type: application/json" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'", "email":"'$EMAIL'"}' \
    $URL/auth/login)

JWT=$(echo $CURL_LOGIN | jq .token)

# delete user
CURL_DELETE=$(curl \
    --silent \
    --request POST \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $JWT" \
    --header "accept: application/json" \
    --data '{"password":"'$PASSWORD'"}' \
    $URL/auth/delete_user)

echo $CURL_DELETE
