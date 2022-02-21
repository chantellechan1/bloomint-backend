from flask import Flask

# db imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def init_db(flask_app: Flask, db_conn_string: str, db_echo: bool) -> None:
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


def create_session():
    new_session = Session()
    return new_session


def init_app(flask_env: str) -> Flask:
    """initializes the app ¯\\_(ツ)_/¯"""
    app = Flask(__name__, instance_relative_config=True)

    if flask_env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        # assume we run development environment
        app.config.from_object('config.DevelopmentConfig')

    # initialize the postgres db
    init_db(flask_app=app, db_conn_string=app.config['DB_CONN_STRING'],
            db_echo=app.config['DB_ECHO'])

    with app.app_context():
        from .auth import routes as auth_routes
        from .plant import routes as plant_routes
        from .static import routes as static_routes

        app.register_blueprint(auth_routes.auth_blueprint)
        app.register_blueprint(plant_routes.plant_blueprint)
        app.register_blueprint(static_routes.static_blueprint)

        return app
