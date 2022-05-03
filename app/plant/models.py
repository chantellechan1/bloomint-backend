from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, null, Text, BINARY
from sqlalchemy.dialects.postgresql import BYTEA

from ..auth import models  # for User model


def init_plants_models(Base):
    global Plant
    global UsersPlants
    global Images
    global UserPlantImages
    global PlantTypeImages

    class Plant(Base):
        __tablename__ = "Plants"

        id = Column(Integer, primary_key=True)
        name = Column(String(512), nullable=False)
        sunlight = Column(String(512), nullable=False)
        min_temp = Column(Integer, nullable=False)  # temperature in Celcius
        max_temp = Column(Integer, nullable=False)  # temperature in Celcius
        # how frequently to water in days
        water_frequency = Column(Integer, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)
        # edible = Column(Boolean, nullable=False)
        # fertilizer_frequency = Column(Integer, nullable=False) # how
        # frequently to fertilize in days

        def __repr__(self):
            return f'<Plant> {self.name}'

    class UsersPlants(Base):
        __tablename__ = "UsersPlants"
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('Users.id'))
        plant_id = Column(Integer, ForeignKey('Plants.id'))
        plant_name = Column(String(256), nullable=True)
        notes = Column(Text, nullable=True)
        purchased_at = Column(DateTime, nullable=True)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<UsersPlants> {self.id}: {self.plant_name}'

    class Images(Base):
        __tablename__ = "Images"
        id = Column(Integer, primary_key=True)
        image = Column(BYTEA, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<Image> {self.id}'

    class UserPlantImages(Base):
        __tablename__ = "UserImages"
        user_plant_id = Column(Integer, primary_key=True, nullable=False)
        image_id = Column(Integer, primary_key=True, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<UserPlantImages> {self.user_plant_id} {self.image_id}'

    class PlantTypeImages(Base):
        __tablename__ = "PlantTypeImages"
        plant_id = Column(Integer, primary_key=True, nullable=False)
        image_id = Column(Integer, primary_key=True, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<PlantTypeImages> {self.user_plant_id} {self.image_id}'
