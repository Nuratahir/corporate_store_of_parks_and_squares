from django.urls import path
from .views import (
    start_page,
    ordering,
    personal_account,
    login,
    registration,
    logout
)

urlpatterns = [
    path("", start_page, name="start_page"),
    path("ordering/", ordering, name="ordering"),
    path("lk/", personal_account, name="personal_account"),
    path("login/", login, name="login"),
    path("registration/", registration, name="registration"),
    path("logout/", logout, name="logout")
]
