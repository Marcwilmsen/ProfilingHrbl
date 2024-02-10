import json
import numpy as np
from .models import SKU, Location, HistoricalResults, PickData_Entries, SessionLocal, WarehouseProfile, WarehouseLocationAssignment, WarehouseSolutionProfile, SolutionLocationAssignment
from sqlalchemy import and_, or_, case, func
from datetime import datetime

import logging


def convert_sku_to_int(result):
    return int(result.lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


def query_skus_with_picks_by_warehouse_profile(profile_name, start_date=None, end_date=None):
    logging.basicConfig(level=logging.INFO)

    with SessionLocal() as session:
        try:
            # Convert start_date and end_date to datetime objects if they are not already
            if start_date and not isinstance(start_date, datetime):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date and not isinstance(end_date, datetime):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Ensure start_date is before end_date
            if start_date and end_date and start_date > end_date:
                raise ValueError("Start date must be before end date.")

            # Modify the query to include all SKUs, even those without picks
            case_statement = case(
                (and_(start_date <= PickData_Entries.date,
                 PickData_Entries.date <= end_date), PickData_Entries.picked),
                else_=0
            )

            query = session.query(
                SKU.inv_sku,
                SKU.country,
                SKU.nbr_of_lanes,
                SKU.constraints,
                func.coalesce(func.sum(case_statement), 0).label('picks')
            ).\
                join(WarehouseLocationAssignment, WarehouseLocationAssignment.sku_id == SKU.inv_sku).\
                join(WarehouseProfile, WarehouseProfile.id == WarehouseLocationAssignment.warehouse_profile_id).\
                filter(WarehouseProfile.name == profile_name).\
                outerjoin(PickData_Entries,
                          PickData_Entries.inventory_sku == SKU.inv_sku)

            results = query.group_by(
                SKU.inv_sku, SKU.country, SKU.nbr_of_lanes, SKU.constraints).all()

            # Initialize lists to collect the data
            ids, countries, picks, nbr_of_lanes, constraints = [], [], [], [], []

            for idx, result in enumerate(results, start=1):
                ids.append(int(result.inv_sku.lstrip(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
                countries.append(result.country)
                picks.append(result.picks)
                nbr_of_lanes.append(result.nbr_of_lanes)
                if result.constraints == "NaN":
                    constraints.append(None)
                else:
                    constraints.append(result.constraints)

                #print(f"SKU: {result.inv_sku}, Country: {result.country}, Picks: {result.picks}, Number of Lanes: {result.nbr_of_lanes}, Contrains: {result.constraints}")

            logging.info(
                f"Number of records fetched: {len(results)} for profile '{profile_name}' from {start_date} to {end_date}")

            return ids, countries, picks, nbr_of_lanes, constraints

        except Exception as e:
            logging.error(
                f"Error in query_skus_with_picks_by_warehouse_profile: {e}")
            session.rollback()
            raise e


def cut_constrains(constrain):
    cut = constrain.split('|')
    if 'NaN' in cut:
        cut = None
    return cut


def load_warehouse_layout(profile_name):
    with SessionLocal() as session:
        try:
            # Define a subquery for warehouse location assignments for the given profile
            wla_subquery = session.query(
                WarehouseLocationAssignment.location_name.label('location'),
                WarehouseLocationAssignment.sku_id
            ).join(
                WarehouseProfile,
                WarehouseProfile.id == WarehouseLocationAssignment.warehouse_profile_id
            ).filter(
                WarehouseProfile.name == profile_name
            ).subquery()

            # Define a query for all locations, left joined with the above subquery
            query = session.query(
                Location.location,
                # Convert -1 to a string
                func.coalesce(wla_subquery.c.sku_id, '-1').label('sku')
            ).outerjoin(
                wla_subquery, Location.location == wla_subquery.c.location
            ).filter(
                or_(
                    Location.location.like('01%'),
                    Location.location.like('03%'),
                    Location.location.like('05%'),
                    Location.location.like('07%'),
                    Location.location.like('09%'),
                    Location.location.like('11%'),
                    Location.location.like('13%'),
                    Location.location.like('15%'),
                    Location.location.like('21%'),
                    Location.location.like('22%'),
                    Location.location.like('31%'),
                    Location.location.like('32%')
                )
            ).order_by(
                Location.location
            )

            # Execute the query and process results
            results = query.all()
            processed_skus = [convert_sku_to_int(
                result.sku) if result.sku != -1 else -1 for result in results]

            return processed_skus

        except Exception as e:
            session.rollback()
            print(f"Error: {e}")  # Print the exception message
            raise e


def query_skus_with_new_and_old_locations(profile_id):
    with SessionLocal() as session:
        try:
            results = session.query(
                SolutionLocationAssignment.sku_id,
                Location.location.label('old_location'),
                SolutionLocationAssignment.location_name.label('new_location')
            ).\
                join(WarehouseSolutionProfile, WarehouseSolutionProfile.id == SolutionLocationAssignment.warehouse_solution_profile_id).\
                join(SKU, SolutionLocationAssignment.sku_id == SKU.inv_sku).\
                join(Location, SolutionLocationAssignment.location_name == Location.location).\
                filter(WarehouseSolutionProfile.id == profile_id).\
                all()

            return [
                {
                    'sku_id': result.sku_id,
                    'old_location': result.old_location,
                    'new_location': result.new_location
                }
                for result in results
            ]

        except Exception as e:
            session.rollback()
            raise e


# def get_historic_results():
#     with SessionLocal() as session:
#         historic_results = session.query(HistoricalResults).order_by(HistoricalResults.id.desc()).limit(9).all()
#         print("DB loaded: ", len(historic_results))
#         solutions = []
#         for result in historic_results:
#             # Assume that result.solution is a JSON string, so we decode it only once
#             solution = json.loads(result.solution)
#             skus = []
#             for x in solution.values():
#                 # Now, solution should be a dict and this should work
#                 if x != -1:
#                     skus.append(convert_sku_to_int(x))
#                 else:
#                     skus.append(x)
#             solutions.append(skus)
#         return solutions


def get_historic_results():
    with SessionLocal() as session:
        historic_results = session.query(HistoricalResults).order_by(HistoricalResults.id.desc()).limit(9).all()
        print("DB loaded: ", len(historic_results))
        solutions = []

        for result in historic_results:
            solution = json.loads(result.solution)
            skus = [convert_sku_to_int(x) if x != -1 else x for x in solution.values()]
            solutions.append(skus)
            print(f"Solution length: {len(skus)}")  # Debugging

        # Check for uniform length
        if len(set(len(sol) for sol in solutions)) > 1:
            print("Error: Inconsistent lengths in historical solutions")
            return []

        return solutions

def get_locations():
    with SessionLocal() as session:
        results = session.query(Location.location, Location.type, Location.side). \
            filter(
                Location.zone.in_([1, 3, 5, 7, 9, 11, 13, 15, 21, 22, 31, 32])
        ).\
            order_by(Location.location.asc()).\
            all()

    locations = []
    location_types = {}
    location_sides = {}
    for result in results:
        locations.append(result[0])
        location_types.update({result[0]: result[1]})
        location_sides.update({result[0]: result[2]})

    # https://numpy.org/doc/stable/reference/generated/numpy.unique.html
    return locations, location_types, location_sides, np.unique(list(location_types.values()))