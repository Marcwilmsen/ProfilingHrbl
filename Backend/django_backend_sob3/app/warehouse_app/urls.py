from django.urls import path
from . import views
from .views import ControlAlgorithmView, PickdataDownloadView, ExportSolutionProfileView, PickdataUploadView, WarehouseSolutionProfileDetailsView, WarehouseSolutionProfilesView, UpdateLocationMatrixView, UpdateMasterListView, ExportCurrentMasterlistProfileView, ExportPickDataView,show_skus_with_new_and_old_locations


urlpatterns = [
    # Upload files and processing endpoints
    path('upload/pickdata/', PickdataUploadView.as_view(),
         name='pickdata-file-upload'),
    path('upload/location_matrix/', UpdateLocationMatrixView.as_view(),
         name='upload-location-matrix'),
    path('upload/new_masterlist/', UpdateMasterListView.as_view(),
         name='upload-new-masterlist'),



    # Download Buttons
    path('download/solution_profile/<int:solution_profile_id>/',
         ExportSolutionProfileView.as_view(), name='download-solution-profile'),
    path('download/masterlist_profile/',
         ExportCurrentMasterlistProfileView.as_view(), name='download-masterlist-profile'),
    path('download/pickdata/',
         PickdataDownloadView.as_view(), name='download-pickdata'),

    # Frontend view endpoints
    path('warehouse-solution-profiles/', WarehouseSolutionProfilesView.as_view(),
         name='warehouse-solution-profiles'),

    path('warehouse-solution-profiles/<int:profile_id>/',
         WarehouseSolutionProfileDetailsView.as_view(), name='warehouse-solution-profile-details'),


     # Algorythm controll views
     path('run-pygad/', ControlAlgorithmView.as_view(), name='run_pygad'),


    path('show-results/', show_skus_with_new_and_old_locations, name='show-results'),
]
###