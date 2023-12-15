import os
from jproperties import Properties
from sqlalchemy import create_engine, Column, Integer, String, DateTime, and_, text
from sqlalchemy.orm import sessionmaker, declarative_base, load_only


def get_session():
    configs = Properties()
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    path = str(CURR_DIR) + '/credentials.properties'
    with open(path, 'rb') as config_file:
        configs.load(config_file)

    user = configs.get("DB_USER").data
    password = configs.get("DB_PASSWORD").data
    host = configs.get("DB_HOST").data
    port = configs.get("DB_PORT").data
    db_name = configs.get("DB_NAME").data

    engine = create_engine('postgresql://' + user + ':' + password
                           + '@' + host + ':'
                           + port + '/' + db_name)
    Session = sessionmaker(bind=engine)
    return Session()


session = get_session()
if session:
    print("Connection to the PostgreSQL established successfully.")
else:
    print("Connection to the PostgreSQL encountered and error.")
Base = declarative_base()


class Location(Base):
    """
        Helper class needed for the database connection to retirieve and build python objects from the database data
    """
    __tablename__ = 'locations'
    locator = Column(String, primary_key=True)
    locator_mirror = Column(String)
    locator_capacity = Column(Integer)


class Skus(Base):
    """
        Helper class needed for the database connection to retirieve and build python objects from the database data
    """
    __tablename__ = ('skus')
    inv_sku = Column(String, primary_key=True)
    country = Column(String)
    sell_sku = Column(String)
    xqty = Column(Integer)
    nbr_of_lanes = Column(Integer)


class PickData(Base):
    """
        Helper class needed for the database connection to retirieve and build python objects from the database data
    """
    __tablename__ = ('pickdata_entries')
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    picked = Column(Integer)
    inventory_sku = Column(String)
    box_number = Column(String)
    pickdata_id = Column(Integer)


def load_products():
    """
        Accessing the Skus table in the database to retirieve all Products from the database.
        Returns ids, id_sku_mapping, id_country

        dbData.py builds python objects. See dbData why no object are created here but only data is returned
    """
    print("products loading")
    id_sku_mapping = {-1: -1}
    id_country = {-1 : ""}
    skus = session.query(Skus).all()
    indexed_rows = list(enumerate(skus, start=1))
    for index, row in indexed_rows:
        id_sku_mapping[index] = row.inv_sku
        id_country[index] = row.country
    ids = list(id_sku_mapping.keys())
    return ids, id_sku_mapping, id_country


def load_pick_data(startDate, endDate, id_sku_mapping):
    """
        Accessing the Pick_data table in the database to retirieve all pickdata entries from the database.
        returns a dictionary containig the product id and the picks per product
        sku_pickdata = { -1: 0, 0:233, 1:4355, ... }

        Setting -1 for empty locations. No product = -1
    """
    print("picks loading")
    sku_pickdata = {-1: 0}
    for id, sku in id_sku_mapping.items():
        sku_pickdata[id] = 0

    picked_data = (session.query(PickData)
                   .filter(and_(PickData.date >= startDate, PickData.date <= endDate))
                   .all())

    for pickdata in picked_data:
        for id, sku in id_sku_mapping.items():
            if pickdata.inventory_sku == sku:
                if id in sku_pickdata.keys():
                    sku_pickdata[id] = sku_pickdata[id] + pickdata.picked
                else:
                    sku_pickdata[id] = pickdata.picked
    return sku_pickdata


def load_locations():
    """
        Accessing the Locations table in the database to retirieve all locations from the database.
        Returns an array of strings for each location
    """
    print("locations loading")
    locations_data = session.execute(text("SELECT locator FROM locations ORDER BY SUBSTRING(locator FROM 3);")).all()

    #locations_data = session.query(Location).order_by(Location.locator).options(load_only(Location.locator)).all()
    locations = []
    for location in locations_data:
        locations.append(location.locator)

    print(locations)
    return locations
