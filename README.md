## Backend

### virtual environments
You should create and activate a virtual environment before doing anything: 

1. `python3 -m venv venv`
2. `source ./venv/bin/activate`

### install dependencies
* on macos, run `brew install postgres` before pip install
`pip install -r requirements.txt`

### running on the server
`python3 wsgi.py`  

### seed dummy database and exit
`python3 wsgi.py --seed-and-exit`  

### How to run the tests in the correct order
MAKE SURE TO USE SOURCE, DONT JUST RUN SET_TEST/SET_PRODUCTION/SET_DEVELOPMENT!!
```
source ./venv/bin/activate
source ./scripts/set_test.sh # set FLASK_ENV to test mode
python3 wsgi.py --seed-and-exit # clear out the test database and put some dummy data in
python3 wsgi.py & # run the server

# various API testing scripts
./scripts/api_test/create_user.sh dummy@gmail.com
./scripts/api_test/plants.sh dummy@gmail.com
./scripts/api_test/delete_user.sh dummy@gmail.com
```

The tests aren't really checking the return values now,
so look at the server output, and make sure everything returned with
a 200 status code. You can also look at the output
of the scripts and make sure they look sane.

### database stuff
db is running on the same EC2 t2.medium instance as the server, db is named hectordb  
installation and setup followed the official postgres 12 docs and also [this tutorial](https://medium.com/amazon-web-services/setting-up-postgresql-on-ubuntu-ec2-server-instead-of-using-rds-part-1-6e5e0b0894fc)  
* on the EC2 instance, it is expected to do `sudo su postgres` before running `psql` to access the db
* alternatively, could do `psql --username=postgres`


### password stuff
generate_password_hash(password, salt_length=128)

### config
Configuration is documented and set in the file config.py
You can change between production/test/development modes as follows:  
```source ./scripts/set_development.sh```  
```source ./scripts/set_test.sh```  
```source ./scripts/set_production.sh```  
