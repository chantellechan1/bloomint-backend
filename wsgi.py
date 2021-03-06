#!/usr/bin/env python3
from app import init_app
from app import utils
import sys
import os

# Make sure the user is running this from the root directory
files_in_cwd = os.listdir(os.getcwd())
if 'wsgi.py' not in files_in_cwd:
    print("Please run this from the root directory:")
    print("python3 wsgi.py ")
    exit(0)

if '--seed-and-exit' in sys.argv:
    seed_and_exit = True
else:
    seed_and_exit = False

flask_env = utils.get_flask_env()
app = init_app(flask_env, seed_and_exit=seed_and_exit)


if __name__ == '__main__':
    if flask_env == utils.FlaskEnv.PRODUCTION:
        app.run(host='0.0.0.0')
    else:
        app.run(host='localhost')
