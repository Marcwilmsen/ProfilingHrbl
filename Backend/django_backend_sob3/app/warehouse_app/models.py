from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON, BigInteger, Boolean, create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')

Base = declarative_base()

# Database credentials and settings..
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', '161.97.173.83')
DB_PORT = os.environ.get('DB_PORT', '5433')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)



class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    location = Column(String, unique=True, index=True)
    zone = Column(Integer)
    level_alfa = Column(String)
    level_num = Column(Integer)
    lane = Column(Integer)
    type = Column(String)
    house = Column(Integer)
    side = Column(String)
    location_status = Column(String)
    locator_capacity = Column(Integer, nullable=True)


class SKU(Base):
    __tablename__ = 'skus'

    # Assuming 'Inv_Sku' is a string, change the type if necessary
    inv_sku = Column(String, primary_key=True)
    sell_sku = Column(String)
    country = Column(String)
    weight = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    stack_box = Column(String)
    xqty = Column(Integer)
    nbr_of_lanes = Column(Integer)
    barcode_enabled = Column(String)
    type = Column(String)
    e_a_carton = Column(Float)
    carton_length = Column(Float)
    carton_width = Column(Float)
    carton_height = Column(Float)
    carton_weight = Column(Float)
    constraints = Column(String)


class Order(Base):
    __tablename__ = 'orders'

    order_number = Column(String, primary_key=True)
    country = Column(String)
    carrier = Column(String)

    boxes = relationship("OrderBox", back_populates="order")
    # One-to-many relationship
    picks = relationship("PickData_Entries", back_populates="order")


class OrderBox(Base):
    __tablename__ = 'order_boxes'

    box_number = Column(String, primary_key=True)
    weight = Column(Float)
    box_name = Column(String)
    order_id = Column(String, ForeignKey('orders.order_number'))

    order = relationship("Order", back_populates="boxes")
    picks = relationship("PickData_Entries", back_populates="box")


class PickData_Entries(Base):
    __tablename__ = 'pickdata_entries'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    picked = Column(Integer)
    inventory_sku = Column(String, ForeignKey('skus.inv_sku'))
    location_code = Column(String, ForeignKey('locations.location'))
    box_number = Column(String, ForeignKey('order_boxes.box_number'))
    pickdata_id = Column(Integer, ForeignKey('pickdata.id'))
    order_number = Column(String, ForeignKey(
        'orders.order_number'))  # Foreign key to Order

    pickdata = relationship("PickData", back_populates="entries")
    box = relationship("OrderBox", back_populates="picks")
    # Many-to-one relationship
    order = relationship("Order", back_populates="picks")


class PickData(Base):
    __tablename__ = 'pickdata'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pickdata_file = Column(String)

    entries = relationship("PickData_Entries", back_populates="pickdata")

# WAREHOUSE PROFILE TABLES
# Corrected WarehouseProfile class....


class WarehouseProfile(Base):
    __tablename__ = 'warehouse_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    creation_timestamp = Column(DateTime)

    # Ensure the relationship is correctly defined
    parameters = relationship("WarehouseParameter",
                              back_populates="warehouse_profile")
    location_assignments = relationship(
        "WarehouseLocationAssignment", backref="related_warehouse_profile")


class WarehouseSolutionProfile(Base):
    __tablename__ = 'warehouse_solution_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    creation_timestamp = Column(DateTime)
    solution_start_parameters = relationship(
        "WarehouseSolutionStartParameter", back_populates="warehouse_solution_profile")
    solution_location_assignments = relationship(
        "SolutionLocationAssignment", backref="related_warehouse_solution_profile")


class WarehouseLocationAssignment(Base):
    __tablename__ = 'warehouse_location_assignments'

    id = Column(Integer, primary_key=True)
    warehouse_profile_id = Column(Integer, ForeignKey('warehouse_profiles.id'))
    location_name = Column(String, ForeignKey('locations.location'))
    sku_id = Column(String, ForeignKey('skus.inv_sku'))

    location = relationship("Location")
    sku = relationship("SKU")
    # Direct relationship to WarehouseProfile
    warehouse_profile = relationship(
        "WarehouseProfile", back_populates="location_assignments")


class SolutionLocationAssignment(Base):
    __tablename__ = 'solution_location_assignments'

    id = Column(Integer, primary_key=True)
    warehouse_solution_profile_id = Column(
        Integer, ForeignKey('warehouse_solution_profiles.id'))
    location_name = Column(String, ForeignKey('locations.location'))
    sku_id = Column(String, ForeignKey('skus.inv_sku'))

    location = relationship("Location")
    sku = relationship("SKU")
    # Direct relationship to WarehouseSolutionProfile
    warehouse_solution_profile = relationship(
        "WarehouseSolutionProfile", back_populates="solution_location_assignments")


class WarehouseParameter(Base):
    __tablename__ = 'warehouse_parameters'
    id = Column(Integer, primary_key=True)
    warehouse_profile_id = Column(Integer, ForeignKey('warehouse_profiles.id'))
    parameter_name = Column(String)
    value = Column(String)
    warehouse_profile = relationship(
        "WarehouseProfile", back_populates="parameters")


class WarehouseSolutionStartParameter(Base):
    __tablename__ = 'warehouse_solution_start_parameters'
    id = Column(Integer, primary_key=True)
    warehouse_solution_profile_id = Column(
        Integer, ForeignKey('warehouse_solution_profiles.id'))
    number_of_generations = Column(Integer)
    algo_from_date = Column(Date)
    algo_too_date = Column(Date)
    day_where_algo_was_started = Column(DateTime)
    percentage_to_stop = Column(Integer)
    warehouse_solution_profile = relationship(
            "WarehouseSolutionProfile", back_populates="solution_start_parameters")

# RESULT TEMP TABLES

class Results(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    generation = Column(BigInteger)
    solution = Column(JSON)
    fitness = Column(String)


class HistoricalResults(Base):
    __tablename__ = 'historicalresults'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    solution = Column(JSON)
    fitness = Column(String)


class ZipZap(Base):
    __tablename__ = 'zipzap'

    id = Column(Integer, primary_key=True)
    historic_result_id = Column(Integer, ForeignKey('historicalresults.id'))
    # Ensure this relationship is correctly defined
    warehouse_solution_profile_id = Column(
        Integer, ForeignKey('warehouse_solution_profiles.id'))

    zipzapentries = relationship("ZipZapEntries", back_populates="zipzap")


class ZipZapEntries(Base):
    __tablename__ = 'zipzapentries'

    id = Column(Integer, primary_key=True)
    zipzap_id = Column(Integer, ForeignKey('zipzap.id'))
    expected = Column(Float)
    actual = Column(Float)
    zipzap = relationship("ZipZap", back_populates="zipzapentries")


class SolutionPicksPerCountryPerMasterArea(Base):
    __tablename__ = 'solution_picks_per_country_per_master_area'
    id = Column(Integer, primary_key=True)
    warehouse_solution_profile_id = Column(
        Integer, ForeignKey('warehouse_solution_profiles.id'))
    historic_result_id = Column(Integer, ForeignKey('historicalresults.id'))

    warehouse_solution_profile = relationship("WarehouseSolutionProfile")
    historical_result = relationship("HistoricalResults")
    entries = relationship(
        "SolutionPicksPerCountryPerMasterAreaEntrys", back_populates="solution_picks")


class SolutionPicksPerCountryPerMasterAreaEntrys(Base):
    __tablename__ = 'solution_picks_per_country_per_master_area_entrys'
    id = Column(Integer, primary_key=True)
    solution_picks_id = Column(Integer, ForeignKey(
        'solution_picks_per_country_per_master_area.id'))
    master_area = Column(String)
    country = Column(String)
    count_picks = Column(Integer)
    solution_picks = relationship(
        "SolutionPicksPerCountryPerMasterArea", back_populates="entries")
