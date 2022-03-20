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

### database stuff
db is running on the same EC2 t2.medium instance as the server, db is named hectordb  
installation and setup followed the official postgres 12 docs and also [this tutorial](https://medium.com/amazon-web-services/setting-up-postgresql-on-ubuntu-ec2-server-instead-of-using-rds-part-1-6e5e0b0894fc)  
* on the EC2 instance, it is expected to do `sudo su postgres` before running `psql` to access the db
* alternatively, could do `psql --username=postgres`


### password stuff
generate_password_hash(password, salt_length=128)


### config
Configuration is documented and set in the file config.py
