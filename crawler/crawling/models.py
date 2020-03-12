from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import relationship

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    #return create_engine(get_project_settings().get("CONNECTION_STRING"))
    return create_engine("{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8".format(
        drivername="mysql+mysqldb",
        user="root",
        passwd="Qwert12@",
        host="docker.for.mac.localhost",
        port="3306",
        db_name="data"))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Part(DeclarativeBase):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True)
    url = Column('url', Text())
    parent_url = Column('parent_url', Text())
    name = Column('name', Text())
    list_price = Column('list_price', Float())
    sale_price = Column('sale_price', Float())
    sku = Column('sku', Text())
    positions = Column('positions', Text())
    other_names = Column('other_names', Text())
    description = Column('description', Text())
    fitments = relationship('Fitment', backref='parts')


class Fitment(DeclarativeBase):
    __tablename__ = 'fitments'

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey('parts.id')) #many fitments for one part
    make = Column('make', Text())
    body_trim = Column('body_trim', Text())
    eng_tran = Column('eng_tran', Text())

#TODO maybe use this to replace sql db helper?
# class Hyundaioemparts(DeclarativeBase):
#     __tablename__ = 'hyundaioemparts'
#
#     id = Column(Integer, primary_key=True)
#     url = Column('url', Text())
#     last_mod_dt = Column('last_mod_dt', DateTime)
#     change_freq = Column('change_freq', Text())
#     priority = Column('priority', Text())
