from sqlalchemy import  Column, ForeignKey, Integer, String, DateTime, Boolean, null

from ..auth import models # for User model

def init_plants_models(Base):
    global Plant
    global UsersPlants

    class Plant(Base):
        __tablename__ = "Plants"

        id = Column(Integer, primary_key=True)
        name = Column(String(512), nullable=False)
        sunlight = Column(String(512), nullable=False)
        min_temp = Column(Integer, nullable=False) # temperature in Celcius
        max_temp = Column(Integer, nullable=False) # temperature in Celcius
        water_frequency = Column(Integer, nullable=False) # how frequently to water in days
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)
        # edible = Column(Boolean, nullable=False)
        # fertilizer_frequency = Column(Integer, nullable=False) # how frequently to fertilize in days

        def __repr__(self):
            return f'<Plant> {self.name}'

    class UsersPlants(Base):
        __tablename__ = "UsersPlants"
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('Users.id'))
        plant_id = Column(Integer, ForeignKey('Plants.id'))
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)
        # purchase_date = Column(DateTime, nullable=False)

        def __repr__(self):
            return f'<UsersPlants> {self.id}'