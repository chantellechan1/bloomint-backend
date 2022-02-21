#!/usr/bin/env python3
from app import init_app
import os


if __name__ == '__main__':
    flask_env = os.environ.get("FLASK_ENV")
    app = init_app(flask_env)
    if flask_env == 'production':
        app.run(host='0.0.0.0')
    else:
        app.run(host='localhost')
