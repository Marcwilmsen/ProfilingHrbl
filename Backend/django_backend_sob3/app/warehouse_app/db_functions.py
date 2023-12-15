import json
from django.db import connection, models
from .models import SKU, Location, Order, OrderBox, PickData, PickData_Entries, SessionLocal, WarehouseProfile,WarehouseLocationAssignment, WarehouseSolutionProfile, SolutionLocationAssignment
from sqlalchemy import func


def convert_sku_to_int(result):
    return int(result.lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


def query_skus_with_picks_by_warehouse_profile(profile_name):
    with SessionLocal() as session:
        try:
            results = session.query(
                SKU.inv_sku,
                SKU.country,
                func.sum(PickData_Entries.picked).label('picks')
            ).\
            join(WarehouseLocationAssignment, WarehouseLocationAssignment.sku_id == SKU.inv_sku).\
            join(WarehouseProfile, WarehouseProfile.id == WarehouseLocationAssignment.warehouse_profile_id).\
            outerjoin(PickData_Entries, PickData_Entries.inventory_sku == SKU.inv_sku).\
            filter(WarehouseProfile.name == profile_name).\
            group_by(SKU.inv_sku, SKU.country).\
            all()

            # Initialize lists to collect the data
            ids, skus, countries, picks = [], [], [], []

            # Iterate through results and populate lists
            for idx, result in enumerate(results, start=1):  # Start counting from 1
                ids.append(int(result.inv_sku.lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))  # Use loop index as the row ID
                skus.append(result.inv_sku)
                countries.append(result.country)
                picks.append(result.picks if result.picks is not None else 0)
                print(f"SKU: {result.inv_sku}, Country: {result.country}, Picks: {result.picks}")


            return ids, skus, countries, picks

        except Exception as e:
            session.rollback()
            raise e


def get_historic_results():
    historic_results = Historicalresults.objects.order_by("-id")[:9]
    print("DB loaded: ", len(historic_results))
    solutions = []
    for result in historic_results:
        test = json.dumps(result.solution)
        solution = json.loads(test)
        skus = []
        for x in solution.values():
            if x != -1:
                skus.append(convert_sku_to_int(x))
            else:
                skus.append(x)
        solutions.append(skus)
    return solutions


def get_locations():
    with SessionLocal() as session:
        results = session.query(Location.location).\
            filter(
                Location.zone.in_([1, 3, 5, 7, 9, 11, 13, 15, 21, 22, 31, 32])
            ).\
            order_by(Location.location.asc()).\
            all()

    locators = [result[0] for result in results]  # Adjusted index to 0
    return locators


class Results(models.Model):
    id = models.AutoField(primary_key=True)
    generation = models.BigIntegerField()
    solution = models.JSONField()
    fitness = models.CharField()

    class Meta:
        managed = False
        db_table = 'results'


class Historicalresults(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    solution = models.JSONField()
    fitness = models.CharField()

    class Meta:
        managed = False
        db_table = 'historicalresults'


