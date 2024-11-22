from django.urls import path
from .views import AcquisitionListView
from .views import AcquisitionDetailView

urlpatterns = [
    path('acquisitions/', AcquisitionListView.as_view(), name='acquisition-list'),
    path('acquisitions/<int:acquisition_id>/', AcquisitionDetailView.as_view(), name='acquisition-detail'),
]
