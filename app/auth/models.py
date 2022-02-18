from sqlalchemy import Column, Integer, String, DateTime


def init_auth_models(Base):
    global User

    class User(Base):
        __tablename__ = 'Users'

        id = Column(Integer, primary_key=True)
        email = Column(String(50), unique=True, nullable=False)
        hashed_password = Column(String(512), nullable=False)
        created_at = Column(DateTime, nullable=False)
        deleted_at = Column(DateTime, nullable=True)

        def __repr__(self):
            return '<User %r>' % self.email
