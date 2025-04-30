from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_form"),
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:id>/", views.event_detail, name="event_detail"),
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),
    path('event/<int:event_id>/rating/create/', views.create_rating, name='create_rating'),
    path('event/<int:event_id>/rating/<int:rating_id>/update/', views.update_rating, name='update_rating'),
    path('event/<int:event_id>/rating/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
    path('event/<int:event_id>/ratings/', views.list_ratings, name='list_ratings'),

]