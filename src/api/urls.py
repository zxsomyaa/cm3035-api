from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("deathrates/", views.deathrates_list),
    path("deathrates/create/", views.deathrates_create),
    path("deathrates/<int:pk>/", views.deathrates_detail),
    path("deathrates/<int:pk>/update/", views.deathrates_update),
    path("deathrates/<int:pk>/delete/", views.deathrates_delete),
    path("deathrates/global-average/", views.global_average_by_year),
]