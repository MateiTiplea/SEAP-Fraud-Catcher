from django.urls import path
from .views import AcquisitionListView, ItemDetailView, ItemsByCpvCodeView, FraudScoreAcquisitionView
from .views import AcquisitionDetailView, ItemsListView

urlpatterns = [
    path('acquisitions/', AcquisitionListView.as_view(), name='acquisition-list'),
    path('acquisitions/<int:acquisition_id>/', AcquisitionDetailView.as_view(), name='acquisition-detail'),
    path('items/', ItemsListView.as_view(), name='item-list'),
    path('items/acquisition_id/<str:acquisition_id>/', ItemDetailView.as_view(), name='item-detail'),
    path('items/cpv_code/<int:cpv_code_id>/', ItemsByCpvCodeView.as_view(), name='items-by-cpv-code'),
    path('items/<str:item_id>/', ItemDetailView.as_view(), name='item-detail'),

    path('acquisitions/<int:acquisition_id>/fraud_score', FraudScoreAcquisitionView.as_view(), name='acquisition-fraud-score'),
]
