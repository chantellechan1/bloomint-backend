from flask import Flask

# db imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def init_db(flask_app: Flask, db_conn_string: str) -> None:
    global engine
    global Base
    global Session

    engine = create_engine(db_conn_string, echo=True)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    from .auth import models as auth_models
    from .plant import models as plant_models

    auth_models.init_auth_models(Base)
    plant_models.init_plants_models(Base)

    Base.metadata.create_all(engine)

def create_session():
    new_session = Session()
    return new_session

def init_app() -> None:
    """initializes the app ¯\_(ツ)_/¯"""
    app = Flask(__name__, instance_relative_config=True)

    # Confused? https://exploreflask.com/en/latest/configuration.html
    # these lines import both config.py and /instance/config.py where all the secrets are stored
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    # initialize the postgres db
    init_db(flask_app=app, db_conn_string=app.config['DB_CONN_STRING'])

    with app.app_context():
        from .auth import routes as auth_routes
        from .plant import routes as plant_routes

        app.register_blueprint(auth_routes.auth_blueprint)
        app.register_blueprint(plant_routes.plant_blueprint)

        return app
