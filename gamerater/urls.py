from django.urls import path

from .models import *
from . import views

app_name = "gamerater"
urlpatterns = [
    path("", views.index, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("game/<int:game_id>", views.game, name="game"),
    path("list/<str:list_name>", views.game_list, name="game_list"),
    path("users/<str:username>/<str:list_name>", views.game_list, name="game_list"),
    path("users/<str:username>", views.user_page, name="users"),
    path("users_dir", views.users_dir, name="users_dir"),
    path("game_db/<int:game_id>", views.game_db, name="game_db"),
]
