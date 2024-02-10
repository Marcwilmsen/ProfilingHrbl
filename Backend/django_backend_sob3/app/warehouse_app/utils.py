from .models import SKU, Location, Order, OrderBox, PickData, PickData_Entries, SessionLocal, WarehouseProfile, WarehouseLocationAssignment
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time
from celery import shared_task
import os
import django
import os
from django.core.files.storage import default_storage
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warehouse_project.settings")
django.setup()
from warehouse_project.send_message_to_frontend import *

from io import StringIO



def verify_pickdata_file_structure(file_content):
    """
    Verifies if the given file content has the expected structure of pickdata file.
    Accepts either bytes or string as file content.
    Returns True if the structure matches the expected header.
    """
    # Decode file_content if it is bytes
    if isinstance(file_content, bytes):
        file_content = file_content.decode()

    uploaded_file = StringIO(file_content)

    # Columns from the updated pickdata.txt
    expected_header = ["row", "Date", "Ordernr", "Boxnr", "Picked", "Location",
                       "Country", "Box Name", "Carrier", "Weight", "Inventory Sku"]

    expected_header_2 = ["", "Date", "Ordernr", "Boxnr", "Picked",
                         "Location", "Country", "Box Name", "Carrier", "Weight", "Inventory Sku"]

    # Reading the header from the uploaded file
    header = uploaded_file.readline().strip().split(',')

    # Reset file pointer to the start for further processing
    uploaded_file.seek(0)

    # Check if all expected columns are present
    return all(col in header for col in expected_header) or all(col in header for col in expected_header_2)


def verify_location_matrix_file_structure(uploaded_file):
    """
    Verifies the structure of the location matrix file against expected header.
    Accepts a file object and returns True if the file structure is as expected.
    """
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
    if all(col in header for col in expected_header):
        send_message_to_all("Location Matrix Filestructure successfully verified.")
        return True
    return False
    


def verify_masterlist_file_structure(uploaded_file):
    """
    Verifies the structure of the masterlist file.
    Accepts an Excel file object and checks against the expected header.
    Returns True if the file structure is valid.
    """
    # Expected columns for the masterlist Excel file
    expected_header = [
        "Sell_sku", "Inv_Sku", "Description", "Country", "Locator",
        "Locator_Mirror", "Weight", "Length", "Width", "Height",
        "Locator_Capacity", "Stack box", "XQty", "NbrOfLanes",
        "Barcode Enabled", "Type", "EA/Carton", "Carton Length",
        "Carton Width", "Carton Height", "Carton Weight", "Constraints"
    ]

    # Read the header from the first sheet of the Excel file
    # nrows=0 reads only the header
    df = pd.read_excel(uploaded_file, sheet_name=0, nrows=0)

    # Extracting the column names from the DataFrame
    header = df.columns.tolist()

    # Check if all expected columns are present
    if all(col in header for col in expected_header):
        send_message_to_all("Masterlist filestructure successfully verified.")
        return True
    return False



def stream_pickdata_txt_file_to_db(pick_data_id, file_data):
    """
    Streams the content of pickdata.txt file to the database.
    Accepts pick_data_id as the database ID and file_data as the content to be streamed.
    """
    with SessionLocal() as session:
        try:
            pick_data_instance = session.query(PickData).get(pick_data_id)
            pick_data_instance.pickdata_file = file_data
            session.commit()
            print("File content streamed to database.")
            send_message_to_all("Successfully uploaded Pickdata.txt fileconted to datanase.")

        except Exception as e:
            send_message_to_all("Error uploading Pickdata.txt filecontend to database.")
            print("Error streaming file content:", e)



@shared_task
def upload_file_to_djang(file_content, original_name):
    """
    Uploads a file to Django's media root.
    The file content and its original name are passed as arguments.
    Returns the full file path where the file is saved.
    """
    # Define a constant filename "Pickdata"
    filename = "Pickdata"
    file_extension = os.path.splitext(original_name)[1]  # Extract the file extension
    # Relative path from MEDIA_ROOT
    relative_file_path = os.path.join('warehouse_app', 'uploads', f"{filename}{file_extension}")

    # Full file path
    full_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)

    # Log the file path
    logger.info(f"File path: {full_file_path}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

    # Save the file using Django's default storage system
    with default_storage.open(relative_file_path, 'wb') as file:
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')  # Encoding string to bytes
        file.write(file_content)
        logger.info(f"File written to {full_file_path}")


    # Additional checks to confirm file saving
    if os.path.exists(full_file_path):
        logger.info(f"File successfully saved at {full_file_path}")
        # Update the database with the file path for the PickData instance with ID 1
        with SessionLocal() as session:
            pick_data_instance = session.query(PickData).get(1)
            if pick_data_instance:
                pick_data_instance.pickdata_file = full_file_path
                session.commit()
                logger.info(f"PickData with ID 1 updated with file path {full_file_path}")
            else:
                logger.error("PickData with ID 1 not found.")
        return full_file_path
    else:
        logger.error(f"File saving failed at {full_file_path}")
        return None



from warehouse_app.models import Base
@shared_task
def process_pickdata_file(file_content, original_name):
    """
    Processes the pickdata file and updates the database.
    The file content and its original name are passed as arguments.
    Handles both string and byte formats of file content.
    """
    try:
        BATCH_SIZE = 10000
        # Check if file_content is bytes and decode it if necessary
        if isinstance(file_content, bytes):
            file_content = file_content.decode()
        # Convert the file content to a StringIO object for easier handling
        uploaded_file = StringIO(file_content)

        # Determine the total number of lines in the file
        total_lines = sum(1 for _ in uploaded_file)
        uploaded_file.seek(0)  # Reset fil

        with SessionLocal() as session:
            try:
                print("STARTING PROCESSING OF PICKDATA")
                send_message_to_all("Start processing pickdata.txt for relational insertion")
                # Deleting and recreating tables
                print("Dropping and recreating tables")
                start_time = time.time()

                # Drop tables
                session.execute(text("DROP TABLE IF EXISTS pickdata_entries CASCADE;"))
                session.execute(text("DROP TABLE IF EXISTS order_boxes CASCADE;"))
                session.execute(text("DROP TABLE IF EXISTS orders CASCADE;"))
                session.execute(text("DROP TABLE IF EXISTS pickdata CASCADE;"))
                session.commit()  # Commit the transaction to ensure tables are dropped

            # Recreate tables
                Base.metadata.create_all(bind=session.get_bind())
                session.commit()  # Commit again to ensure tables are created

                end_time = time.time()
                print(f"Tables dropped and recreated in {end_time - start_time} seconds.")
                print(
                    f"Deleted old pickdata via dropping tables and recreacted tables completed in {end_time - start_time} seconds.")
                send_message_to_all(f"Deleted old pickdata completed in {end_time - start_time} seconds.")
                print("Start processing and insertino process:")
                start_time = time.time()  # Start timing
                # Create and commit a placeholder PickData object
                pick_data_instance = PickData(name="Pickdata")
                # Convert file content back to bytes if it's a string
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')

                # Start the file upload task
                upload_file_to_djang.apply_async(args=[file_content, "Pickdata"])
                session.add(pick_data_instance)
                session.commit()

                uploaded_file.seek(0)
                # Read the header to determine the file structure
                header = uploaded_file.readline().strip().split(',')

                # Determine if the file uses the second structure
                print(header[0])
                    # Determine if the file uses the second structure
                using_second_structure = header[0] == '' and len(header) == 11

                print("second file struct:", using_second_structure)
                seen_skus = set(val[0] for val in session.query(SKU.inv_sku).all())
                seen_locations = set(
                    val[0] for val in session.query(Location.location).all())
                seen_orders = set(val[0]
                                for val in session.query(Order.order_number).all())
                seen_boxes = set(val[0] for val in session.query(
                    OrderBox.box_number).all())

                new_skus = []
                new_locations = []
                new_orders = []
                new_boxes = []
                pick_entries = []

                for index, line in enumerate(uploaded_file, start=1):
                    # Split line and adjust for file structure
                    split_line = line.strip().split(',')

                    _, date_str, order_number, box_number, picked, location_code, country, box_name, carrier, weight, inventory_sku = split_line

                    try:
                        if using_second_structure:
                            date = datetime.strptime(date_str, '%Y-%m-%d')

                        else:
                            date = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
                    except ValueError:
                        continue

                    if order_number not in seen_orders:
                        new_orders.append(
                            Order(order_number=order_number, country=country, carrier=carrier))
                        seen_orders.add(order_number)

                    if box_number not in seen_boxes:
                        new_boxes.append(OrderBox(
                            box_number=box_number, order_id=order_number, box_name=box_name, weight=weight))
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
                        order_number=order_number,
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
                            send_message_to_all("Integrity Error: " + ie)
                            # Here, you can decide what to do. For instance, you can rollback, or skip this batch.
                            session.rollback()

                        # Print the last ID of the PickData_Entries
                        last_pick_entry = session.query(PickData_Entries).order_by(
                            PickData_Entries.id.desc()).first()
                        if last_pick_entry:
                            progress_percentage = (index / total_lines) * 100
                            message = f"Processing: Line {index}/{total_lines} ({progress_percentage:.2f}%)"
                            print(message)
                            send_message_to_all(message)
                            print(
                                f"After {index} lines, last PickData_Entries ID: {last_pick_entry.id}")

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

                    end_time = time.time()  # End timing
                    print(
                        f"Successfully processed pickdata update completed in {end_time - start_time} seconds.")
                    send_message_to_all(f"Successfully inserted remaining lines and processed pickdata update. Completed in {end_time - start_time} seconds.")
                    
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
    except Exception as e:
        logger.error(f"Error in process_pickdata_file: {e}")
        raise e


def process_location_matrix_file(uploaded_file):
    """
    Processes the location matrix file and updates the database.
    Accepts a file object representing the location matrix file.
    """
    start_time = time.time()  # Start timing

    with SessionLocal() as session:
        # Skip header
        lines = uploaded_file.readlines()[1:]

        # Fetch all existing locations into a dictionary for quick lookup
        existing_locations = {
            loc.location: loc for loc in session.query(Location).all()}

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
    send_message_to_all(
        f"Location Matrix file processing completed in {end_time - start_time} seconds.")
    print(f"Process completed in {end_time - start_time} seconds.")


def process_masterlist(uploaded_file):
    """
    Processes the masterlist file and updates the database.
    Accepts an Excel file object representing the masterlist.
    """
    start_time = time.time()
    send_message_to_all("Starting to processing new masterlist into the database.")
    try:
        read_start = time.time()
        masterlist_df = pd.read_excel(
            uploaded_file, sheet_name=0, skipfooter=0)  # Remove skipfooter option
        masterlist_records = masterlist_df.to_dict(orient='records')
        read_end = time.time()
        print(f"Excel file read in {read_end - read_start} seconds.")
        print(
            f"Total rows in Excel (excluding header): {len(masterlist_records)}")
    except Exception as e:
        send_message_to_all(f"Error reading the masterlist Excel file: {e}")
        raise ValueError(f"Error reading the Excel file: {e}")

    with SessionLocal() as session:
        try:
            # Delete existing entries related to the masterlist
            warehouse_profile = session.query(WarehouseProfile).filter_by(name="masterlist").first()
            if warehouse_profile:
                # Delete related location assignments
                for assignment in warehouse_profile.location_assignments:
                    session.delete(assignment)
                
                # Delete the warehouse profile itself
                session.delete(warehouse_profile)
                session.commit()


            preload_start = time.time()
            locations_cache = {
                location.location: location for location in session.query(Location).all()}
            skus_cache = {sku.inv_sku: sku for sku in session.query(SKU).all()}
            assignments_cache = {(assignment.sku_id, assignment.warehouse_profile_id): assignment for assignment in session.query(WarehouseLocationAssignment).all()}
            preload_end = time.time()
            print(
                f"Preloading data completed in {preload_end - preload_start} seconds.")

            profile_start = time.time()
            warehouse_profile = session.query(
                WarehouseProfile).filter_by(name="masterlist").first()
            if not warehouse_profile:
                warehouse_profile = WarehouseProfile(
                    name="masterlist", creation_timestamp=datetime.now())
                session.add(warehouse_profile)
                session.commit()
            profile_end = time.time()
            print(
                f"Warehouse profile processing completed in {profile_end - profile_start} seconds.")

            processing_start = time.time()
            processed_skus = set()
            skipped_rows = 0
            for index, row in enumerate(masterlist_records, start=1):
                try:
                    process_masterlist_row(
                        session, row, locations_cache, skus_cache, assignments_cache, warehouse_profile)
                    processed_skus.add(row['Inv_Sku'])
                except ValueError as e:
                    print(f"Row {index} processing error: {e}")
                    skipped_rows += 1
            processing_end = time.time()
            print(
                f"Row processing completed in {processing_end - processing_start} seconds.")
            print(f"Total SKUs processed: {len(processed_skus)}")
            print(f"Total SKUs skipped: {skipped_rows}")

            for assignment in assignments_cache.values():
                session.merge(assignment)

            commit_start = time.time()
            session.commit()
            commit_end = time.time()
            print(
                f"Database commit completed in {commit_end - commit_start} seconds.")
            
        except Exception as e:
            send_message_to_all(f"An error occured while processing the masterlist: {e}")
            session.rollback()
            raise e

    end_time = time.time()
    print(f"Total processing time: {end_time - start_time} seconds.")
    send_message_to_all(f"Successfully processed new masterlist into database in {end_time - start_time} seconds")


def update_sku_fields(sku, row):
    """
    Updates the fields of a SKU object based on data from a row dictionary.
    Accepts an SKU object and a dictionary containing SKU data.
    """
    # Update SKU fields from row
    sku.sell_sku = row['Sell_sku']
    sku.country = row['Country']
    sku.weight = row['Weight']
    sku.length = row['Length']
    sku.width = row['Width']
    sku.height = row['Height']
    sku.stack_box = row['Stack box']
    sku.xqty = None if pd.isna(row['XQty']) else row['XQty']
    sku.nbr_of_lanes = None if pd.isna(
        row['NbrOfLanes']) else row['NbrOfLanes']
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
    """
    Creates a new SKU object based on data from a row dictionary.
    Accepts a dictionary containing SKU data and returns a new SKU object.
    """
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


def process_assignment(row, assignments_cache, warehouse_profile, sku, location):
    """
    Processes an assignment for the warehouse location.
    Accepts a row dictionary, cache of assignments, warehouse profile, SKU, and location objects.
    """
    assignment_key = (sku.inv_sku, warehouse_profile.id)

    if assignment_key in assignments_cache:
        assignment = assignments_cache[assignment_key]
        assignment.location_name = location.location  # Update location if it has changed
    else:
        new_assignment = WarehouseLocationAssignment(
            warehouse_profile_id=warehouse_profile.id,
            location_name=location.location,
            sku_id=sku.inv_sku
        )
        assignments_cache[assignment_key] = new_assignment


def process_masterlist_row(session, row, locations_cache, skus_cache, assignments_cache, warehouse_profile):
    """
    Processes a single row of the masterlist file.
    Accepts the database session, a row dictionary, caches of locations and SKUs, assignments cache, and the warehouse profile.
    """
    locator = row['Locator']
    if locator not in locations_cache:
        raise ValueError(f"Location {locator} not found.")
    location = locations_cache[locator]
    location.locator_capacity = None if pd.isna(
        row['Locator_Capacity']) else row['Locator_Capacity']

    inv_sku = row['Inv_Sku']
    sku = skus_cache.get(inv_sku)
    if sku:
        update_sku_fields(sku, row)
    else:
        sku = create_sku(row)
        session.add(sku)
        skus_cache[inv_sku] = sku

    process_assignment(row, assignments_cache,
                       warehouse_profile, sku, location)


