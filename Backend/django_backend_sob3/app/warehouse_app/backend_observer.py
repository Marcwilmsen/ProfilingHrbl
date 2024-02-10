import json
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warehouse_project.settings")
django.setup()
from sqlalchemy import text
from datetime import datetime
from .models import SessionLocal, HistoricalResults ,Results, Location, WarehouseSolutionProfile, ZipZap, ZipZapEntries, SolutionPicksPerCountryPerMasterArea, SolutionPicksPerCountryPerMasterAreaEntrys, SolutionLocationAssignment, WarehouseSolutionStartParameter
import time
from warehouse_project.send_message_to_frontend import *
from sqlalchemy.exc import OperationalError
from django.dispatch import Signal

# Define the signal without providing_args
websocket_message_signal = Signal()
class Observer():
    def __init__(self):
        self.batched_generations = []
        self.batch_size = 100  # Number of generations to batch before insertion
        self.location_cache = None
        self.last_insert_time = None  # Track the last insert time


    def load_location_cache(self):
        with SessionLocal() as session:
            self.location_cache = set(session.query(Location.location).all())

    def convert_to_SKU(self, sku_idxs):
        skus = []
        for sku_idx in sku_idxs:
            if sku_idx == -1:
                skus.append(-1)
            else:
                skus.append(f"A{int(sku_idx):03d}")
        return skus

    def getResult(self, message):
        result = Results()
        result.generation = message.get("generation")
        solution_dict = dict(zip(message.get("locations"),
                             self.convert_to_SKU(message.get("solution"))))
        result.solution = json.dumps(solution_dict)
        result.fitness = message.get("solution_fitness")
        return result

    def getHistoricalresult(self, message):
        result = HistoricalResults()
        result.date = datetime.today().strftime('%Y-%m-%d')
        solution_dict = dict(zip(message.get("locations"),
                             self.convert_to_SKU(message.get("solution"))))
        result.solution = json.dumps(solution_dict)
        result.fitness = message.get("solution_fitness")
        #print(message.get("distribution_per_zone_per_country"))
        return result

    def getWarehouseSolutionLocationAssignments(self, solution_dict, warehouse_solution_profile):
        if self.location_cache is None:
            self.load_location_cache()

        # Pre-filter SKUs
        filtered_solution_dict = {k: v for k,
                                  v in solution_dict.items() if v != -1}

        return [
            SolutionLocationAssignment(
                warehouse_solution_profile_id=warehouse_solution_profile.id,
                location_name=location_name,
                sku_id=f"A{int(sku_value):03d}" if sku_value >= 0 else None
            )
            for location_name, sku_value in filtered_solution_dict.items()
            if (location_name,) in self.location_cache
        ]

    def createGenerationWithEntrys(self, message):
        with SessionLocal() as session:
            try:
                solution_generation_profile = WarehouseSolutionProfile(
                    name=f"Generation_{message.get('generation')}",
                    creation_timestamp=datetime.now()
                )
                session.add(solution_generation_profile)
                session.commit()

                solution_dict = dict(
                    zip(message.get("locations"), message.get("solution")))
                warehouse_location_assignments = self.getWarehouseSolutionLocationAssignments(
                    solution_dict, solution_generation_profile)

                # Adjusting batch size for optimized bulk save
                batch_size = 2000  # Example batch size, adjust based on performance
                for i in range(0, len(warehouse_location_assignments), batch_size):
                    batch = warehouse_location_assignments[i:i+batch_size]
                    session.bulk_save_objects(batch)
                    session.commit()

                return True

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")
                raise
            finally:
                session.close()

    def createFinalSolutionWithEntrys(self, message):
        with SessionLocal() as session:
            try:
                print("Starting session...")

                # Create WarehouseSolutionProfile
                solution_generation_profile = WarehouseSolutionProfile(
                    name=f"Solution_{datetime.today()}",
                    creation_timestamp=datetime.now()
                )
                # Print the profile details
                #print(f"Creating WarehouseSolutionProfile: {solution_generation_profile}")
                session.add(solution_generation_profile)
                session.commit()
                # Prepare and add ZoneEntries
                solution_dict = dict(
                    zip(message.get("locations"), message.get("solution")))
                # Print the solution dictionary
                #print(f"Solution Dict: {solution_dict}")
                warehouse_location_assingments = self.getWarehouseSolutionLocationAssignments(
                    solution_dict, solution_generation_profile)
                # Print assignments
                #print(f"Warehouse Location Assignments: {warehouse_location_assingments}")
                session.bulk_save_objects(
                    warehouse_location_assingments)  # Bulk operation
                session.commit()  # Committing after bulk operations
                return solution_generation_profile.id

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")  # Print the error
                raise e
            finally:
                session.close()
                print("Session closed")  # Confirm session closure

    def insert_solution_picks_data(self, message, solution_profile_id, historic_result_id):
        with SessionLocal() as session:
            try:
                # Create SolutionPicksPerCountryPerMasterArea record
                solution_picks = SolutionPicksPerCountryPerMasterArea(
                    warehouse_solution_profile_id=solution_profile_id,
                    historic_result_id=historic_result_id
                )
                session.add(solution_picks)
                session.commit()

                # Process and insert entries for each master area and country
                distribution_dict = message.get("distribution_per_country", {})
                for master_area, countries in distribution_dict.items():
                    for country, count in countries.items():
                        entry = SolutionPicksPerCountryPerMasterAreaEntrys(
                            solution_picks_id=solution_picks.id,
                            master_area=master_area,
                            country=country,
                            count_picks=count
                        )
                        session.add(entry)
                session.commit()

                print("Successfully inserted solution picks data.")

            except Exception as e:
                session.rollback()
                print(
                    f"An error occurred while inserting solution picks data: {e}")
                send_message_to_all(f"An error occurred while inserting solution picks data: {e}")
                raise


    def insertZipZaps(self, historic_result_id, solution_profile_id, message):
        with SessionLocal() as session:
            print("im in insert zip zap")
            zipzapss = message.get("zipzap", {})
            print("ZIP ZAP: ", zipzapss)
            try:
                # Create WarehouseSolutionProfile
                zipzap = ZipZap(
                    historic_result_id=historic_result_id,
                    warehouse_solution_profile_id=solution_profile_id
                    )
                session.add(zipzap)
                session.commit()

                for expected, current in message["zipzap"]:
                    print("zap expected: ", expected, " current: ", current)
                    zipzapentry = ZipZapEntries(
                    zipzap_id=zipzap.id,
                    expected=expected,
                    actual=current
                    )
                    session.add(zipzapentry)
                session.commit()
                print(f"Successfully inserted zipzap data")

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")
                send_message_to_all(f"An error occurred while trying to insert the solution zipzap data: {e}")
                raise e
            finally:
                session.close()


    def update(self, message):
      # Logic to handle the message from pygad
        if message.get("result_type") == "FINAL_result":
            processing_start = time.time()
            print("Final message received")

            # Create a new session and test the connection
            session = SessionLocal()
            try:
                # Test the connection using text-based SQL
                session.execute(text('SELECT 1'))
            except OperationalError:
                print("Database connection failed, trying to reconnect")
                session = SessionLocal()  # Try to establish a new session
                session.execute(text('SELECT 1'))  # Re-test the connection


            print("Backend distribution_per_zone_per_country received: ",
                  message.get("distribution_per_zone_per_country"))
            print("Fitness: ", message["solution_fitness"])
            print("Picks: ", message["distribution_per_country"])
            print("Print distribution_per_country: ",
                  message["distribution_per_country"])
            print("Print ZipZaps: ",
                  message.get("zipzap"))
            
            current_time = datetime.now()
                # Check if we have a last insert time and if it's within 5 seconds
            print("current time:", current_time,  " last innsert time:", self.last_insert_time)
            if self.last_insert_time and (current_time - self.last_insert_time).total_seconds() < 5:
                print("SKIPPING insertion, last insertion was less than 5 seconds ago.")
                return None  # Or however you'd like to handle the skip
            

            try:
                #store historic result as json (not relational)
                result = self.getHistoricalresult(message)
                session.add(result)
                session.commit() 
                # RELATIONAL INSERT
                solution_profile_id = self.createFinalSolutionWithEntrys(message)
                if isinstance(solution_profile_id, int):
                    highest_end_start_row = session.query(WarehouseSolutionStartParameter).order_by(WarehouseSolutionStartParameter.id.desc()).first()

                    print("before ifhigheststart row:", highest_end_start_row.number_of_generations)
                    if highest_end_start_row:
                            # Update the start row with the solution profile ID
                            # Ensure the model has a field to store the solution_profile_id
                        print("higheststart row:", highest_end_start_row.number_of_generations)
                        highest_end_start_row.warehouse_solution_profile_id = solution_profile_id
                        session.commit()

                    # Insert solution picks data
                    self.insert_solution_picks_data(
                        message, solution_profile_id, result.id)
                    self.insertZipZaps(result.id, solution_profile_id, message)

                    self.last_insert_time = current_time  # Update the last insert time after successful insertion
                    processing_end = time.time()
                    print(f"successfully processed final result insert: {solution_profile_id} in  {processing_end - processing_start} seconds.")
                    send_message_to_all(f"successfully processed final result insert: {solution_profile_id} in  {processing_end - processing_start} seconds.")

            except Exception as e:
                print(f"An error occurred while trying to insert the solution: {e}")
                send_message_to_all(f"An error occurred while trying to insert the solution: {e}")

                session.rollback()
            finally:
                session.close()
                processing_end = time.time()
                print(f"Processing completed in {processing_end - processing_start} seconds")
                send_message_to_all(f"Processing completed in {processing_end - processing_start} seconds")


        elif message.get("result_type") == "MID_result":
            print(f"GENERATION: {message.get('generation')}")
            rounded_percentage = round(float(message.get('progess_in_percent')), 2)
            send_message_to_all(f"{rounded_percentage}% - GENERATION: {message.get('generation')} OF  {message.get('max_generations')}")

