import json

from asgiref.sync import sync_to_async
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .serializers import FileUploadSerializer
from .utils import verify_pickdata_file_structure,verify_location_matrix_file_structure, process_pickdata_file, process_location_matrix_file, process_masterlist,verify_masterlist_file_structure, verify_generation_json_structure_from_file

from django.http import JsonResponse
import subprocess
from .db_functions import query_skus_with_picks_by_warehouse_profile, get_locations, get_historic_results
import Herb_PyGAD.main as pygad
import Herb_PyGAD.testData as testData
import random
from .backend_observer import Observable


class PickdataUploadView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            name = serializer.validated_data['name']

            # Verify structure of the file
            if not verify_pickdata_file_structure(uploaded_file):
                return Response({"detail": "Invalid file structure."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Process and populate the database
            process_pickdata_file(uploaded_file, name)

            return Response({"detail": "File processed successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            process_location_matrix_file(uploaded_file, name)

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
        


def run_pygad(request):
    # Security checks should go here (e.g., authentication)
    skus_ids, skus, countries, picks = query_skus_with_picks_by_warehouse_profile('masterlist')
    # Taking only the first country from the split country string for each sku_id
    countries_dict = {sku_id: country_str.split('/')[:-1] for sku_id, country_str in zip(skus_ids, countries)}
    locations = get_locations()
    pick_data = dict(zip(skus_ids, picks))
    pick_data[-1] = 0
    historic_results = get_historic_results()

    while len(locations) != len(skus_ids):
        skus_ids.append(-1)

    initial_population = []

    for sku in historic_results:
        print("Type: ", type(sku))
        print("SKU: ", sku)
        initial_population.append(sku)

    print("initial_pop from db: ", len(initial_population))

    while len(initial_population) != 10:
        initial_population.append(random.sample(list(skus_ids), len(skus_ids)))

    print("initial_pop with shuffle: ", len(initial_population))

    backend = Observable()

    # Call the script and get the output
    pygad.run_ga(initial_population, skus_ids, locations, countries_dict, pick_data,
                 testData.country_groups_for_area, backend, 100)

    # Return the output in a JSON response
    return JsonResponse({
        'output': None,
        'error': None
    })