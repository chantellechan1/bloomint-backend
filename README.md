## Backend

### virtual environments
You should create and activate a virtual environment before doing anything: 

1. `python3 -m venv venv`
2. `source ./venv/bin/activate`

### install dependencies
`pip install -r requirements.txt`
* on macos, run `brew install postgres` before pip install

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
Two config files are expected, one is public and located in `./config`. There is a private config file located in `./instance/config.py`.
The expected contents of this file are below:  
```
PEPPER = ''
JWT_SECRET = ''
DB_PASSWORD = ''
DB_HOST = '<your db host ip address>'
DB_CONN_STRING = f'postgresql://postgres:{DB_PASSWORD}@{DB_HOST}:<your db port, postgres defaults to 5432>/<your db name>'
```
* note: the length of the `PEPPER` is reccommend by the NIST to be minimum 14 characters. However, the length of the password and the pepper combined cannot exceed 128 characters otherwise the error `ValueError: [digital envelope routines: CRYPTO_internal] bad key length` will be generated on macOS operating systems.
* due to this limitation, the pepper length for this project is expected to be 14 characters, and the minimum and maximum password lengths are `7` characters and `100` characters respectively
