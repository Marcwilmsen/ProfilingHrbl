from django.urls import path
from . import views
from .views import PickdataUploadView, UpdateLocationMatrixView, UpdateMasterListView, run_pygad


urlpatterns = [
    path('upload/pickdata/', PickdataUploadView.as_view(), name='pickdata-file-upload'),
    path('upload/location_matrix/', UpdateLocationMatrixView.as_view(), name='upload-location-matrix'),
    path('upload/new_masterlist/', UpdateMasterListView.as_view(), name='upload-new-masterlist'),
    path('run-pygad/', run_pygad, name='run_pygad'),
]
