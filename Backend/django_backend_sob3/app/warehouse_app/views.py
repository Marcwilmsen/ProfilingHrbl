import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.http import FileResponse, HttpResponse
from sqlalchemy import asc
from .serializers import FileUploadSerializer
from .utils import verify_pickdata_file_structure, verify_location_matrix_file_structure, process_pickdata_file, process_location_matrix_file, process_masterlist, verify_masterlist_file_structure
from .models import SKU, Location,WarehouseSolutionStartParameter , PickData, SessionLocal, WarehouseProfile, WarehouseSolutionProfile, SolutionLocationAssignment, WarehouseLocationAssignment
from django.http import JsonResponse
import pandas as pd
from io import BytesIO
from .db_functions import query_skus_with_new_and_old_locations
import datetime
from django.core.files.storage import default_storage
from warehouse_app.backend_observer import websocket_message_signal
from warehouse_project.send_message_to_frontend import send_message_to_all
import logging
from warehouse_app.run_pygad_algo import run_algorithm
from django.core.cache import cache
from celery import current_app
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

logger = logging.getLogger(__name__)
import os

pickdata_processing = None
class ControlAlgorithmView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data if request.body else {}

        # Retrieve the current task ID from cache
        current_task_id = cache.get('algorithm_task_id')

        # If a task is already running, revoke it
        if current_task_id:
            current_app.control.revoke(current_task_id, terminate=True)

        # Start the new task
        task = run_algorithm.delay(data)
        print("Algorithm started asynchronously")

        # Store the new task ID in the cache
        cache.set('algorithm_task_id', task.id)

        # Returning the new task ID to track its status if needed
        return Response({"status": "Algorithm restarted", "task_id": task.id}, status=201)



class PickdataUploadView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            name = serializer.validated_data['name']

            # Read the file contents
            file_content = uploaded_file.read()

            # Verify structure of the file
            if not verify_pickdata_file_structure(file_content):
                return Response({"detail": "Invalid file structure."}, status=status.HTTP_400_BAD_REQUEST)

            # Start the process with file content
            print("starting pickdata process")
            # Retrieve the current task ID from cache
            current_task_id = cache.get('pickdata_task_id')

            # If a task is already running, revoke it
            if current_task_id:
                current_app.control.revoke(current_task_id, terminate=True)

            # Start the new task
            send_message_to_all("Starting pickdata process asynchronously")
            task = process_pickdata_file.delay(file_content,name )
            print("Processing pickdata started asynchronously")

            # Store the new task ID in the cache
            cache.set('pickdata_task_id', task.id)
            return Response({"status": "File processing task has started successfully with id:", "task_id: ": task.id }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class PickdataDownloadView(APIView):
    def get(self, request):
        session = SessionLocal()
        try:
            # Query using SQLAlchemy session
            pickdata_entry = session.query(PickData).filter(PickData.id == 1).first()

            if pickdata_entry and pickdata_entry.pickdata_file:
                file_path = pickdata_entry.pickdata_file

                # Check if file exists in default storage
                if default_storage.exists(file_path):
                    file = default_storage.open(file_path, 'rb')
                    response = FileResponse(file, content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
                else:
                    logger.error(f"File not found at path: {file_path}")
                    return Response({"detail": "File not found."}, status=404)
            else:
                logger.error("No PickData entry found with name 'Pickdata'")
                return Response({"detail": "No file available for download."}, status=404)
        except Exception as e:
            logger.exception("Error in PickdataDownloadView")
            return Response({"detail": str(e)}, status=500)
        finally:
            session.close()

class UpdateLocationMatrixView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            name = serializer.validated_data['name']

            # Verify structure of the file
            if not verify_location_matrix_file_structure(uploaded_file):
                return Response({"detail": "Invalid file structure."}, status=status.HTTP_400_BAD_REQUEST)
            print("file structure verified!")
            # Process and populate the database
            process_location_matrix_file(uploaded_file)

            return Response({"detail": "File processed successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateMasterListView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            name = serializer.validated_data['name']

            # Verify structure of the file
            if not verify_masterlist_file_structure(uploaded_file):
                return Response({"detail": "Invalid file structure."}, status=status.HTTP_400_BAD_REQUEST)
            print("file structure verified!")
            # Process and populate the database
            try:
                process_masterlist(uploaded_file)
                return Response({"detail": "File processed successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Log the exception or handle it as needed
                print(f"Error processing file: {e}")
                return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportSolutionProfileView(APIView):
    def get(self, request, solution_profile_id):
        with SessionLocal() as session:
            # Fetch the solution profile based on ID
            solution_profile = session.query(WarehouseSolutionProfile).filter(
                WarehouseSolutionProfile.id == solution_profile_id
            ).first()
            if not solution_profile:
                return HttpResponse("Solution profile not found.", status=404)

            # Fetch the related location assignments
            solution_location_assignments = session.query(
                SolutionLocationAssignment, SKU, Location
            ).join(SKU).join(Location).filter(
                SolutionLocationAssignment.warehouse_solution_profile_id == solution_profile_id
            ).order_by(SKU.inv_sku).all()  # Order by SKU ID

            # Prepare the data for Excel export
            data = [{
                'Sell_sku': sku.sell_sku if sku.sell_sku is not None else "",
                'Inv_Sku': sku.inv_sku if sku.inv_sku is not None else "",
                'Description': "",  # Replace with the actual description field if it exists
                'Country': sku.country if sku.country is not None else "",
                'Locator': location.location if location.location is not None else "",
                'Locator_Mirror': "",  # Assuming mirror locator is the same
                'Weight': sku.weight if sku.weight is not None else "",
                'Length': sku.length if sku.length is not None else "",
                'Width': sku.width if sku.width is not None else "",
                'Height': sku.height if sku.height is not None else "",
                'Locator_Capacity': location.locator_capacity if location.locator_capacity is not None else "",
                'Stack box': sku.stack_box if sku.stack_box is not None else "",
                'XQty': sku.xqty if sku.xqty is not None else "",
                'NbrOfLanes': sku.nbr_of_lanes if sku.nbr_of_lanes is not None else "",
                'Barcode Enabled': sku.barcode_enabled if sku.barcode_enabled is not None else "",
                'Type': sku.type if sku.type is not None else "",
                'EA/Carton': sku.e_a_carton if sku.e_a_carton is not None else "",
                'Carton Length': sku.carton_length if sku.carton_length is not None else "",
                'Carton Width': sku.carton_width if sku.carton_width is not None else "",
                'Carton Height': sku.carton_height if sku.carton_height is not None else "",
                'Carton Weight': sku.carton_weight if sku.carton_weight is not None else "",
                'Constraints': sku.constraints if sku.constraints is not None else ""
            } for assignment, sku, location in solution_location_assignments]

            # Create a pandas DataFrame and write to an Excel file
            df = pd.DataFrame(data)
            df = df.fillna('')  # Replace NaN with empty strings
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='SolutionProfile')

            # Prepare the HTTP response with the Excel file
            response = HttpResponse(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="solution_profile_{solution_profile_id}.xlsx"'
            return response


class ExportCurrentMasterlistProfileView(APIView):
    def get(self, request):
        with SessionLocal() as session:
            # Fetch the solution profile based on ID
            warehouse_masterlist_profile = session.query(WarehouseProfile).filter(
                WarehouseProfile.name == 'masterlist'
            ).first()
            if not warehouse_masterlist_profile:
                return HttpResponse("Warehouse masterlist profile not found.", status=404)

            # Fetch the related location assignments
            warehouse_masterlist_location_assignments = session.query(
                WarehouseLocationAssignment, SKU, Location
            ).join(SKU).join(Location).filter(
                WarehouseLocationAssignment.warehouse_profile_id == warehouse_masterlist_profile.id
            ).order_by(SKU.inv_sku).all()  # Order by SKU ID

            # Prepare the data for Excel export
            data = [{
                'Sell_sku': sku.sell_sku if sku.sell_sku is not None else "",
                'Inv_Sku': sku.inv_sku if sku.inv_sku is not None else "",
                'Description': "",  # Replace with the actual description field if it exists
                'Country': sku.country if sku.country is not None else "",
                'Locator': location.location if location.location is not None else "",
                'Locator_Mirror': "",  # Assuming mirror locator is the same
                'Weight': sku.weight if sku.weight is not None else "",
                'Length': sku.length if sku.length is not None else "",
                'Width': sku.width if sku.width is not None else "",
                'Height': sku.height if sku.height is not None else "",
                'Locator_Capacity': location.locator_capacity if location.locator_capacity is not None else "",
                'Stack box': sku.stack_box if sku.stack_box is not None else "",
                'XQty': sku.xqty if sku.xqty is not None else "",
                'NbrOfLanes': sku.nbr_of_lanes if sku.nbr_of_lanes is not None else "",
                'Barcode Enabled': sku.barcode_enabled if sku.barcode_enabled is not None else "",
                'Type': sku.type if sku.type is not None else "",
                'EA/Carton': sku.e_a_carton if sku.e_a_carton is not None else "",
                'Carton Length': sku.carton_length if sku.carton_length is not None else "",
                'Carton Width': sku.carton_width if sku.carton_width is not None else "",
                'Carton Height': sku.carton_height if sku.carton_height is not None else "",
                'Carton Weight': sku.carton_weight if sku.carton_weight is not None else "",
                'Constraints': sku.constraints if sku.constraints is not None else ""
            } for assignment, sku, location in warehouse_masterlist_location_assignments]

            # Create a pandas DataFrame and write to an Excel file
            df = pd.DataFrame(data)
            df = df.fillna('')  # Replace NaN with empty strings
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='SolutionProfile')

            # Prepare the HTTP response with the Excel file
            response = HttpResponse(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="masterlist_{datetime.datetime.now()}.xlsx"'
            return response


class ExportPickDataView(APIView):
    def get(self, request):
        with SessionLocal() as session:
            # Fetch the PickData object based on a specific condition or ID
            pick_data_instance = session.query(PickData).filter(
                PickData.name == 'Pickdata.txt'  # Replace with your actual condition
            ).first()

            if not pick_data_instance:
                return HttpResponse("Pickdata file not found.", status=404)

            # Fetch the file content from the PickData instance
            pickdata_file_content = pick_data_instance.pickdata_file

            # Prepare the HTTP response with the file content
            response = HttpResponse(
                pickdata_file_content,
                content_type='text/plain'
            )
            response['Content-Disposition'] = f'attachment; filename="pickdata_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"'
            return response


class WarehouseSolutionProfilesView(APIView):
    def get(self, request):
        with SessionLocal() as session:
            # Filter profiles that start with "Solution"
            profiles = session.query(WarehouseSolutionProfile).filter(
                WarehouseSolutionProfile.name.like('Solution%')
            ).all()

            data = [{
                'id': profile.id,
                'name': profile.name,
                'timestamp': profile.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S") if profile.creation_timestamp else None
            } for profile in profiles]

            return Response(data, status=status.HTTP_200_OK)

class WarehouseSolutionProfileDetailsView(APIView):
    def get(self, request, profile_id):
        with SessionLocal() as session:
            # Fetch the masterlist profile
            masterlist_profile = session.query(WarehouseProfile).filter(
                WarehouseProfile.name == 'masterlist'
            ).first()

            if not masterlist_profile:
                return HttpResponse("Masterlist profile not found.", status=404)

            # Fetch the specific solution profile
            solution_profile = session.query(WarehouseSolutionProfile).filter(
                WarehouseSolutionProfile.id == profile_id
            ).first()

            if not solution_profile:
                return HttpResponse("Solution profile not found.", status=404)

            # Fetch start data for the solution profile
            solution_start_data = session.query(WarehouseSolutionStartParameter).filter(
                WarehouseSolutionStartParameter.warehouse_solution_profile_id == solution_profile.id
            ).first()

            start_data = None
            if solution_start_data:
                start_data = {
                    'number_of_generations': solution_start_data.number_of_generations,
                    'algo_from_date': solution_start_data.algo_from_date,
                    'algo_too_date': solution_start_data.algo_too_date,
                    'percentage_to_stop': solution_start_data.percentage_to_stop,
                    'day_where_algo_was_started': solution_start_data.day_where_algo_was_started
                }

            # Fetch location assignments for masterlist and solution profile
            masterlist_assignments = session.query(WarehouseLocationAssignment).filter(
                WarehouseLocationAssignment.warehouse_profile_id == masterlist_profile.id
            ).all()

            solution_assignments = session.query(SolutionLocationAssignment).filter(
                SolutionLocationAssignment.warehouse_solution_profile_id == solution_profile.id
            ).order_by(asc(SolutionLocationAssignment.sku_id)).all()

            data = []
            for solution_assignment in solution_assignments:
                masterlist_location = next(
                    (assignment.location_name for assignment in masterlist_assignments if assignment.sku_id == solution_assignment.sku_id), None)
                data.append({
                    'sku_id': solution_assignment.sku_id,
                    'masterlist_location': masterlist_location,
                    'solution_location': solution_assignment.location_name
                })
            print("start data", start_data)
            response_data = {
                'start_data': start_data,
                'assignments': data
            }
            return Response(response_data, status=status.HTTP_200_OK)


def show_skus_with_new_and_old_locations(request, profile_id=1):
    try:
        data = query_skus_with_new_and_old_locations(profile_id)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Define the receiver function for the signal
def send_websocket_message(sender, **kwargs):
    message = kwargs.get('message', '')
    if message:
        try:
            send_message_to_all(message)
            logger.info(f"WebSocket message sent: {message}")
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")

# Connect the receiver function to the signal
websocket_message_signal.connect(send_websocket_message)