from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import BYTEA


def init_plants_models(Base):
    global PlantType
    global UserPlant
    global Image
    global UserPlantImage
    global PlantTypeImage

    class PlantType(Base):
        """
        Represents a species/type of plant. For example, 'Mint' plants in general.
        Contains info that is relevate to all plants of that type.
        """
        __tablename__ = "PlantType"

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

    class UserPlant(Base):
        """
        Represents a plant that is actually owned by somebody.
        Of course, it must have an associated plant type
        """
        __tablename__ = "UserPlant"
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('User.id'))
        planttype_id = Column(Integer, ForeignKey('PlantType.id'))
        plant_name = Column(String(256), nullable=True)
        notes = Column(Text, nullable=True)
        purchased_at = Column(DateTime, nullable=True)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<UsersPlants> {self.id}: {self.plant_name}'

    class Image(Base):
        """
        Represents an image. Of anything.
        """
        __tablename__ = "Image"
        id = Column(Integer, primary_key=True)
        image = Column(BYTEA, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<Image> {self.id}'

    class UserPlantImage(Base):
        """
        Represents a picture of a user plant type.
        (a plant someone owns)
        """
        __tablename__ = "UserImage"
        user_plant_id = Column(Integer, primary_key=True, nullable=False)
        image_id = Column(Integer, primary_key=True, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<UserPlantImages> {self.user_plant_id} {self.image_id}'

    class PlantTypeImage(Base):
        """
        Represents a picture of a plant type.
        (a generic 'stock image' of a plant)
        """
        __tablename__ = "PlantTypeImage"
        plant_id = Column(Integer, primary_key=True, nullable=False)
        image_id = Column(Integer, primary_key=True, nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return f'<PlantTypeImages> {self.user_plant_id} {self.image_id}'
