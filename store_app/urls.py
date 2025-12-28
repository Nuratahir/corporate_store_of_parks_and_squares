from django.urls import path
from .views import (
    start_page,
    ordering,
    personal_account,
    login,
    registration,
    logout,
    add_to_cart,
    update_quantity,
    remove_item,
)

urlpatterns = [
    path("", start_page, name="start_page"),
    path("add-to-cart/", add_to_cart, name="add_to_cart"),
    path("ordering/", ordering, name="ordering"),
    path("update-quantity/<int:item_id>/", update_quantity, name="update_quantity"),
    path("remove-item/<int:item_id>/", remove_item, name="remove_item"),
    path("lk/", personal_account, name="personal_account"),
    path("login/", login, name="login"),
    path("registration/", registration, name="registration"),
    path("logout/", logout, name="logout"),
]
