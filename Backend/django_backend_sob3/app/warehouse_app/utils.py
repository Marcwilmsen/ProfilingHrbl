from .models import SKU, Location, Order, OrderBox, PickData, PickData_Entries, SessionLocal, WarehouseProfile, WarehouseSolutionProfile, SolutionLocationAssignment,WarehouseLocationAssignment
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pandas as pd
import json
from datetime import datetime
import time

def verify_pickdata_file_structure(uploaded_file):
    # Columns from the updated pickdata.txt
    expected_header = ["row", "Date", "Ordernr", "Boxnr", "Picked", "Location",
                       "Country", "Box Name", "Carrier", "Weight", "Inventory Sku"]
    
    expected_header_2 = ["","Date","Ordernr","Boxnr","Picked","Location","Country","Box Name","Carrier","Weight","Inventory Sku"]

    # Reading the header from the uploaded file
    header = uploaded_file.readline().decode().strip().split(',')

    # Reset file pointer to the start for further processing
    uploaded_file.seek(0)

    # Check if all expected columns are present
    return all(col in header for col in expected_header) or all(col in header for col in expected_header_2)


def verify_location_matrix_file_structure(uploaded_file):
    # Columns from the updated pickdata.txt
    expected_header = ["LocationId", "LocationName", "Zone", "Level_alfa", "Level_num", "Lane",
                       "Type", "House", "Side", "LocationStatus"]

    # Reading the header from the uploaded file
    header = uploaded_file.readline().decode().strip().split(',')
    print(header)
    header[0] = header[0].replace('\ufeff', '')
    print(header)
    print(expected_header)
    # Reset file pointer to the start for further processing
    uploaded_file.seek(0)

    # Check if all expected columns are present
    return all(col in header for col in expected_header)

def verify_masterlist_file_structure(uploaded_file):
    # Expected columns for the masterlist Excel file
    expected_header = [
        "Sell_sku", "Inv_Sku", "Description", "Country", "Locator", 
        "Locator_Mirror", "Weight", "Length", "Width", "Height", 
        "Locator_Capacity", "Stack box", "XQty", "NbrOfLanes", 
        "Barcode Enabled", "Type", "EA/Carton", "Carton Length", 
        "Carton Width", "Carton Height", "Carton Weight", "Constraints"
    ]

    # Read the header from the first sheet of the Excel file
    df = pd.read_excel(uploaded_file, sheet_name=0, nrows=0)  # nrows=0 reads only the header

    # Extracting the column names from the DataFrame
    header = df.columns.tolist()

    # Check if all expected columns are present
    return all(col in header for col in expected_header)
import json

def verify_generation_json_structure_from_file(file_obj):
    try:
        # Move to the start of the file
        file_obj.seek(0)

        # Read the entire file content in binary, then decode to string
        file_content_binary = file_obj.read()
        file_content = file_content_binary.decode('utf-8').strip('"').replace('\\n', '\n').replace('\\"', '"')

        # Load the JSON data from the modified content
        data = json.loads(file_content)

        # Check if data is a list
        if not isinstance(data, list):
            return False

        # Check the structure of the first generation, if available
        if len(data) > 0:
            first_gen = data[0]

            # Check for 'generation' and 'solution' keys in the first generation
            if 'generation' not in first_gen or 'solution' not in first_gen:
                return False

            # Check if 'solution' is a dictionary
            if not isinstance(first_gen['solution'], dict):
                return False

        return True

    except Exception as e:
        # Handle invalid JSON data and other exceptions
        print(f"Error in JSON structure verification: {e}")
        return False


def process_pickdata_file(uploaded_file, name):
    BATCH_SIZE = 50000

    with SessionLocal() as session:
        try:
            print("STARTING PROCESSING OF PICKDATA")
            # Create and add a new PickData instance
            pick_data_instance = PickData(name=name)
            session.add(pick_data_instance)
            session.commit()
            # Read the header to determine the file structure
            header = uploaded_file.readline().decode().strip().split(',')

            # Determine if the file uses the second structure
            print(header[0])
            using_second_structure = header[0] == '' and len(header) == 11

            # Skip header
            #uploaded_file.readline()


            print("second file struct:", using_second_structure)
            seen_skus = set(val[0] for val in session.query(SKU.inv_sku).all())
            seen_locations = set(val[0] for val in session.query(Location.location).all())
            seen_orders = set(val[0] for val in session.query(Order.order_number).all())
            seen_boxes = set(val[0] for val in session.query(OrderBox.box_number).all())

            new_skus = []
            new_locations = []
            new_orders = []
            new_boxes = []
            pick_entries = []

            for index, line in enumerate(uploaded_file, start=1):
                    # Split line and adjust for file structure
                split_line = line.decode().strip().split(',')

                _, date_str, order_number, box_number, picked, location_code, country, box_name, carrier, weight, inventory_sku = split_line

                try:
                    if using_second_structure:
                        date = datetime.strptime(date_str, '%Y-%m-%d')  

                    else:
                        date = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')  
                except ValueError:
                    continue


                if order_number not in seen_orders:
                    new_orders.append(Order(order_number=order_number, country=country, carrier=carrier))
                    seen_orders.add(order_number)

                if box_number not in seen_boxes:
                    new_boxes.append(OrderBox(box_number=box_number, order_id=order_number, box_name=box_name, weight=weight))
                    seen_boxes.add(box_number)


                # Create SKU if it doesn't exist
                if inventory_sku not in seen_skus:
                    new_sku = SKU(inv_sku=inventory_sku)
                    new_skus.append(new_sku)
                    seen_skus.add(inventory_sku)

                # Create Location if it doesn't exist
                if location_code not in seen_locations:
                    new_location = Location(location=location_code)
                    new_locations.append(new_location)
                    seen_locations.add(location_code)


                pick_entries.append(PickData_Entries(
                    date=date,
                    picked=picked,
                    inventory_sku=inventory_sku,
                    location_code=location_code,
                    box_number=box_number,
                    pickdata_id=pick_data_instance.id
                ))

                # Commit every BATCH_SIZE entries
                if index % BATCH_SIZE == 0:
                    try:
                        session.bulk_save_objects(new_skus)
                        session.bulk_save_objects(new_locations)
                        session.bulk_save_objects(new_orders)
                        session.bulk_save_objects(new_boxes)
                        session.bulk_save_objects(pick_entries)
                        session.commit()
                    except IntegrityError as ie:
                        print("Integrity Error:", ie)
                        # Here, you can decide what to do. For instance, you can rollback, or skip this batch.
                        session.rollback()

                    # Print the last ID of the PickData_Entries
                    last_pick_entry = session.query(PickData_Entries).order_by(PickData_Entries.id.desc()).first()
                    if last_pick_entry:
                        print(f"After {index} lines, last PickData_Entries ID: {last_pick_entry.id}")

                    new_skus.clear()
                    new_locations.clear()
                    new_orders.clear()
                    new_boxes.clear()
                    pick_entries.clear()

            # Commit any remaining entries
            if new_skus or new_locations or new_orders or new_boxes or pick_entries:
                session.bulk_save_objects(new_skus)
                session.bulk_save_objects(new_locations)
                session.bulk_save_objects(new_orders)
                session.bulk_save_objects(new_boxes)
                session.bulk_save_objects(pick_entries)
                session.commit()
                print("Inserted remaining lines")

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()



def process_location_matrix_file(uploaded_file, name):
    start_time = time.time()  # Start timing

    with SessionLocal() as session:
        # Skip header
        lines = uploaded_file.readlines()[1:]

        # Fetch all existing locations into a dictionary for quick lookup
        existing_locations = {loc.location: loc for loc in session.query(Location).all()}

        for line in lines:
            # Extract data from the line
            _, location, zone, level_alfa, level_num, lane, type_, house, side, location_status = line.decode().strip().split(',')

            # Convert numeric fields to integers
            level_num = int(level_num) if level_num else None
            lane = int(lane) if lane else None
            house = int(house) if house else None
            zone = int(zone) if zone else None

            # Check if the location already exists
            existing_location = existing_locations.get(location)

            if existing_location:
                # Update existing location
                existing_location.zone = zone
                existing_location.level_alfa = level_alfa
                existing_location.level_num = level_num
                existing_location.lane = lane
                existing_location.type = type_
                existing_location.house = house
                existing_location.side = side
                existing_location.location_status = location_status
            else:
                # Create a new Location instance and add it to the session
                new_location = Location(
                    location=location,
                    zone=zone,
                    level_alfa=level_alfa,
                    level_num=level_num,
                    lane=lane,
                    type=type_,
                    house=house,
                    side=side,
                    location_status=location_status
                )
                session.add(new_location)

        try:
            session.commit()  # Committing here to save changes
        except Exception as e:
            session.rollback()  # Rollback in case of any error
            raise e
        finally:
            session.close()  # Close the session

    end_time = time.time()  # End timing
    print(f"Process completed in {end_time - start_time} seconds.")


def process_masterlist(uploaded_file):
    start_time = time.time()

    # Efficiently read Excel file into a dictionary
    try:
        read_start = time.time()
        masterlist_df = pd.read_excel(uploaded_file, sheet_name=0).to_dict(orient='records')
        read_end = time.time()
        print(f"Excel file read in {read_end - read_start} seconds.")
    except Exception as e:
        raise ValueError(f"Error reading the Excel file: {e}")

    with SessionLocal() as session:
        try:
            preload_start = time.time()
            # Preload all locations, SKUs, and assignments
            locations_cache = {location.location: location for location in session.query(Location).all()}
            skus_cache = {sku.inv_sku: sku for sku in session.query(SKU).all()}
            assignments_cache = {(assignment.sku_id, assignment.warehouse_profile_id): assignment 
                                 for assignment in session.query(WarehouseLocationAssignment).all()}
            preload_end = time.time()
            print(f"Preloading data completed in {preload_end - preload_start} seconds.")

            # Process WarehouseProfile named "masterlist"
            profile_start = time.time()
            warehouse_profile = session.query(WarehouseProfile).filter_by(name="masterlist").first()
            if not warehouse_profile:
                warehouse_profile = WarehouseProfile(name="masterlist", creation_timestamp=datetime.now())
                session.add(warehouse_profile)
                session.commit()
            else:
                session.query(WarehouseLocationAssignment).filter_by(warehouse_profile_id=warehouse_profile.id).delete()

            profile_end = time.time()
            print(f"Warehouse profile processing completed in {profile_end - profile_start} seconds.")

            processing_start = time.time()
            # Initialize a new assignments cache after deleting old assignments
            assignments_cache = {}
            for row in masterlist_df:
                # Process each row (Location, SKU, Assignment)
                process_masterlist_row(session, row, locations_cache, skus_cache, assignments_cache, warehouse_profile)
            processing_end = time.time()
            print(f"Row processing completed in {processing_end - processing_start} seconds.")

            # Commit once after processing all rows
            commit_start = time.time()
            print("Start inserging masterlist rows!")
            session.commit()
            commit_end = time.time()
            print(f"Database commit completed in {commit_end - commit_start} seconds.")

        except Exception as e:
            session.rollback()
            raise e

    end_time = time.time()
    print(f"Total processing time: {end_time - start_time} seconds.")

def update_sku_fields(sku, row):
    # Update SKU fields from row
    sku.sell_sku = row['Sell_sku']
    sku.country = row['Country']
    sku.weight = row['Weight']
    sku.length = row['Length']
    sku.width = row['Width']
    sku.height = row['Height']
    sku.stack_box = row['Stack box']
    sku.xqty = None if pd.isna(row['XQty']) else row['XQty']
    sku.nbr_of_lanes = None if pd.isna(row['NbrOfLanes']) else row['NbrOfLanes']
    sku.barcode_enabled = row['Barcode Enabled']
    sku.type = row['Type']
    sku.e_a_carton = row['EA/Carton']
    sku.carton_length = row['Carton Length']
    sku.carton_width = row['Carton Width']
    sku.carton_height = row['Carton Height']
    sku.carton_weight = row['Carton Weight']
    sku.constraints = row['Constraints']
    # Add other fields as necessary

def create_sku(row):
    # Create and return a new SKU object with all fields
    return SKU(
        inv_sku=row['Inv_Sku'],
        sell_sku=row['Sell_sku'],
        country=row['Country'],
        weight=row['Weight'],
        length=row['Length'],
        width=row['Width'],
        height=row['Height'],
        stack_box=row['Stack box'],
        xqty=None if pd.isna(row['XQty']) else row['XQty'],
        nbr_of_lanes=None if pd.isna(row['NbrOfLanes']) else row['NbrOfLanes'],
        barcode_enabled=row['Barcode Enabled'],
        type=row['Type'],
        e_a_carton=row['EA/Carton'],
        carton_length=row['Carton Length'],
        carton_width=row['Carton Width'],
        carton_height=row['Carton Height'],
        carton_weight=row['Carton Weight'],
        constraints=row['Constraints']
        # Add other fields as necessary
    )


def process_assignment(session, warehouse_profile, sku, location, assignments_cache):
    # Create or update WarehouseLocationAssignment
    assignment_key = (sku.inv_sku, warehouse_profile.id)
    if assignment_key in assignments_cache:
        assignment = assignments_cache[assignment_key]
        assignment.location_name = location.location
    else:
        assignment = WarehouseLocationAssignment(
            warehouse_profile_id=warehouse_profile.id, 
            location_name=location.location, 
            sku_id=sku.inv_sku
        )
        session.add(assignment)
        assignments_cache[assignment_key] = assignment

def process_masterlist_row(session, row, locations_cache, skus_cache, assignments_cache, warehouse_profile):
    # Process Location
    locator = row['Locator']
    if locator not in locations_cache:
        raise ValueError(f"Location {locator} not found.")
    location = locations_cache[locator]

    # Update locator capacity if present
    location.locator_capacity = None if pd.isna(row['Locator_Capacity']) else row['Locator_Capacity']

    # Process SKU
    inv_sku = row['Inv_Sku']
    sku = skus_cache.get(inv_sku)
    if sku:
        update_sku_fields(sku, row)
    else:
        sku = create_sku(row)
        session.add(sku)
        skus_cache[inv_sku] = sku

    # Process WarehouseLocationAssignment´
    #print("WAREHOUSE PROFILE ID", warehouse_profile.id)
    process_assignment(session, warehouse_profile, sku, location, assignments_cache)
