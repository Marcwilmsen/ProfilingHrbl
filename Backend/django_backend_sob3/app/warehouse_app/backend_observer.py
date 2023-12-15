import json
from .db_functions import Results, Historicalresults
from datetime import datetime
from .models import SKU, Location, Order, OrderBox, PickData, PickData_Entries, SessionLocal, WarehouseProfile,  WarehouseSolutionProfile, ZipZap, ZipZapEntries, SolutionPicksPerCountryPerMasterArea, SolutionPicksPerCountryPerMasterAreaEntrys, WarehouseLocationAssignment, SolutionLocationAssignment
import time


class Observable():
    def __init__(self):
        self.batched_generations = []
        self.batch_size = 100  # Number of generations to batch before insertion
        self.location_cache = None

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
        print("Generation: ", message.get("generation"))
        result.generation = message.get("generation")
        solution_dict = dict(zip(message.get("locations"),
                             self.convert_to_SKU(message.get("solution"))))
        result.solution = json.dumps(solution_dict)
        result.fitness = message.get("solution_fitness")
        return result

    def getHistoricalresult(self, message):
        result = Historicalresults()
        result.date = datetime.today().strftime('%Y-%m-%d')
        solution_dict = dict(zip(message.get("locations"),
                             self.convert_to_SKU(message.get("solution"))))
        result.solution = json.dumps(solution_dict)
        result.fitness = message.get("solution_fitness")
        print(message.get("distribution_per_zone_per_country"))
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
                print("Starting session...")  # To confirm the session starts

                # Create WarehouseSolutionProfile
                solution_generation_profile = WarehouseSolutionProfile(
                    name=f"Solution_{datetime.today()}",
                    creation_timestamp=datetime.now()
                )
                # Print the profile details
                print(
                    f"Creating WarehouseSolutionProfile: {solution_generation_profile}")

                session.add(solution_generation_profile)
                session.commit()

                # Prepare and add ZoneEntries
                solution_dict = dict(
                    zip(message.get("locations"), message.get("solution")))
                # Print the solution dictionary
                print(f"Solution Dict: {solution_dict}")

                warehouse_location_assingments = self.getWarehouseSolutionLocationAssignments(
                    solution_dict, solution_generation_profile)
                # Print assignments
                print(
                    f"Warehouse Location Assignments: {warehouse_location_assingments}")

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
                raise

    def createBatchGenerationWithEntrys(self, batched_messages):
        with SessionLocal() as session:
            try:
                # Bulk operation for adding assignments
                for message in batched_messages:
                    solution_dict = dict(
                        zip(message.get("locations"), message.get("solution")))
                    warehouse_location_assignments = self.getWarehouseSolutionLocationAssignments(
                        solution_dict, WarehouseSolutionProfile(
                            name=f"Generation_{message.get('generation')}", creation_timestamp=datetime.now())
                    )
                    session.bulk_save_objects(warehouse_location_assignments)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")
                raise
            finally:
                session.close()

    def update(self, message):
        # Logic to handle the message from pygad
        if message.get("result_type") == "FINAL_result":
            processing_start = time.time()
            print("Final message received")

            print("Backend distribution_per_zone_per_country received: ",
                  message.get("distribution_per_zone_per_country"))
            print("Fitness: ", message["solution_fitness"])
            print("Picks: ", message["distribution_per_country"])
            print("Print distribution_per_country: ",
                  message["distribution_per_country"])
            result = self.getHistoricalresult(message)
            result.save()
            print("Saved Historical Result!")
            # RELATIONAL INSERT
            processing_start = time.time()
            solution_profile_id = self.createFinalSolutionWithEntrys(message)

            if isinstance(solution_profile_id, int):
                print("successfully processed final result insert: ",
                      solution_profile_id)
                # Insert solution picks data
                self.insert_solution_picks_data(
                    message, solution_profile_id, result.id)

                with SessionLocal() as session:
                    try:
                        # Create WarehouseSolutionProfile
                        zipzap = ZipZap(
                            historic_result_id=result.id,
                            warehouse_solution_profile_id=solution_profile_id
                        )
                        session.add(zipzap)
                        session.commit()

                        for expected, current in message["zipzap"]:
                            zipzapentries = ZipZapEntries(
                                zipzap_id=zipzap.id,
                                expected=expected,
                                actual=current
                            )
                            session.add(zipzapentries)
                        session.commit()
                        processing_end = time.time()
                        print(
                            f"Solution DB insertion:  {processing_end - processing_start} seconds.")

                    except Exception as e:
                        session.rollback()
                        print(f"An error occurred: {e}")
                        raise e
                    finally:
                        session.close()

        elif message.get("result_type") == "MID_result":
            processing_start = time.time()

            # result = self.getResult(message)
            # result.save()

            self.batched_generations.append(message)
            if len(self.batched_generations) >= self.batch_size:
                processing_start = time.time()
                self.createBatchGenerationWithEntrys(self.batched_generations)
                self.batched_generations = []  # Reset the batch
                processing_end = time.time()
                print(
                    f"Batched solution DB insertion: {processing_end - processing_start} seconds.")

            processing_end = time.time()
            print(
                f"GENERATION DB insertion:  {processing_end - processing_start} seconds.")

        else:
            print("Something went wrong bro")
