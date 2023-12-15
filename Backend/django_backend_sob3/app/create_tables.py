import sys
import os
sys.path.append(os.path.abspath('.'))

from warehouse_app.models import Base, engine

def create_tables():
    """This function creates tables in the database."""
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
