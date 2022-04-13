from django.urls import path
from django.views.generic import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns
from githubprojects import views


urlpatterns = [
    path('', RedirectView.as_view(url='/projects/')),
    path('projects/', views.ProjectList.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)