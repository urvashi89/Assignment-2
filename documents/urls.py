from django.urls import path

from .views import (
    DocumentListCreateView,
    DocumentDetailView,
    QueryCreateView,
    QueryHistoryView,
)

urlpatterns = [
    path("documents/", DocumentListCreateView.as_view()),
    path("documents/<int:pk>/", DocumentDetailView.as_view()),
     path("queries/", QueryHistoryView.as_view(), name="query-history"),
    path("query/", QueryCreateView.as_view()),
]