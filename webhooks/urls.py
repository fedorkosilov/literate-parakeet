from django.urls import path
from django.views.generic import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns
from webhooks import views


urlpatterns = [
    path('webhooks/', views.WebhookList.as_view(), name='webhook-list'),
    path('webhooks/<int:pk>/', views.WebhookDetail.as_view(), name='webhook-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)