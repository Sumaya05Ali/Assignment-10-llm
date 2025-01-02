from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
def init_db():
    DATABASE_URL = "postgresql://user:password@db:5432/shared_db"
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
# Hotel model
class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    rating = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    room_type = Column(String)
    price = Column(Float)
    image = Column(String)  # Image path reference

    city_id = Column(Integer, ForeignKey('cities.id'))
    city = relationship('City', back_populates='hotels')

# City model
class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    hotels = relationship('Hotel', back_populates='city')


