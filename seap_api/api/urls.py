from django.urls import path
from .views import AcquisitionListView, ItemDetailView
from .views import AcquisitionDetailView, ItemsListView

urlpatterns = [
    path('acquisitions/', AcquisitionListView.as_view(), name='acquisition-list'),
    path('acquisitions/<int:acquisition_id>/', AcquisitionDetailView.as_view(), name='acquisition-detail'),
    path('items/', ItemsListView.as_view(), name='item-list'),
    path('items/acquisition_id/<str:acquisition_id>/', ItemDetailView.as_view(), name='item-detail'),
]
