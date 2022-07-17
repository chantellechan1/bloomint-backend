from flask import Flask
from flask_cors import CORS

# db imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from . import utils

import datetime
import sys


def init_db(db_conn_string: str, db_echo: bool) -> None:
    global engine
    global Base
    global Session

    engine = create_engine(db_conn_string, echo=db_echo)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    from .auth import models as auth_models
    from .plant import models as plant_models

    auth_models.init_auth_models(Base)
    plant_models.init_plants_models(Base)

    Base.metadata.create_all(engine)


def seed_db_for_test(db) -> None:
    """
    This will clear out the entire database,
    and may fill it with dummy data.
    FOR TESTING/DEVELOPMENT ONLY
    """
    if utils.get_flask_env() == utils.FlaskEnv.PRODUCTION:
        raise Exception("Do not seed production database!")

    trans = db.begin()
    # clear out the database
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())

    # add dummy plant types
    from .plant import models as plant_models
    mint = plant_models.PlantType(
        name='mint',
        sunlight='medium',
        min_temp=0,
        max_temp=22,
        water_frequency=10,
        created_at=datetime.datetime.utcnow())
    basil = plant_models.PlantType(
        name='basil',
        sunlight='high',
        min_temp=10,
        max_temp=26,
        water_frequency=8,
        created_at=datetime.datetime.utcnow())
    db.add(mint)
    db.add(basil)

    trans.commit()


def create_session() -> Session:
    new_session = Session()
    return new_session


def init_app(flask_env: str, seed_and_exit: bool) -> Flask:
    """initializes the app ¯\\_(ツ)_/¯"""
    app = Flask(__name__, instance_relative_config=True)

    # CORS
    CORS(app, supports_credentials=True)

    flask_env = utils.get_flask_env()
    if flask_env == utils.FlaskEnv.PRODUCTION:
        app.config.from_object('config.ProductionConfig')
        print("Running in PRODUCTION mode")
    elif flask_env == utils.FlaskEnv.TEST:
        app.config.from_object('config.TestConfig')
        print("Running in TEST mode")
    elif flask_env == utils.FlaskEnv.DEVELOPMENT:
        app.config.from_object('config.DevelopmentConfig')
        print("Running in DEVELOPMENT mode")
    else:
        raise Exception(f"unkown flask environment: {flask_env}")

    # initialize the postgres db
    init_db(db_conn_string=app.config['DB_CONN_STRING'],
            db_echo=app.config['DB_ECHO'])

    if seed_and_exit:
        seed_db_for_test(create_session())
        sys.exit(0)

    with app.app_context():
        from .auth import routes as auth_routes
        from .plant import routes as plant_routes
        from .static import routes as static_routes

        app.register_blueprint(auth_routes.auth_blueprint)
        app.register_blueprint(plant_routes.plant_blueprint)
        app.register_blueprint(static_routes.static_blueprint)

        return app
