from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"), path("signup/", views.signup, name="signup"),
    path("trips/", views.trip_list, name="trip_list"), path("trips/new/", views.trip_create, name="trip_create"),
    path("trips/<int:pk>/", views.trip_detail, name="trip_detail"), path("trips/<int:pk>/edit/", views.trip_edit, name="trip_edit"),
    path("trips/<int:pk>/delete/", views.trip_delete, name="trip_delete"), path("dashboard/", views.dashboard, name="dashboard"),
    path("trips/<int:pk>/itinerary/new/", views.itinerary_item_create, name="itinerary_item_create"),
    path("trips/<int:pk>/itinerary/<int:item_pk>/edit/", views.itinerary_item_edit, name="itinerary_item_edit"),
    path("trips/<int:pk>/itinerary/<int:item_pk>/delete/", views.itinerary_item_delete, name="itinerary_item_delete"),
    path("trips/<int:pk>/packing/add/", views.packing_item_create, name="packing_item_create"),
    path("trips/<int:pk>/packing/<int:item_pk>/toggle/", views.packing_item_toggle, name="packing_item_toggle"),
    path("trips/<int:pk>/packing/<int:item_pk>/delete/", views.packing_item_delete, name="packing_item_delete"),
    path("trips/<int:pk>/expenses/new/", views.expense_create, name="expense_create"),
    path("trips/<int:pk>/expenses/<int:expense_pk>/edit/", views.expense_edit, name="expense_edit"),
    path("trips/<int:pk>/expenses/<int:expense_pk>/delete/", views.expense_delete, name="expense_delete"),
    path("trips/<int:pk>/sharing/", views.trip_sharing, name="trip_sharing"),
    path("trips/<int:pk>/sharing/<int:member_pk>/remove/", views.trip_unshare, name="trip_unshare"),
]
