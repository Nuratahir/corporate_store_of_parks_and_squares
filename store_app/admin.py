from django.contrib import admin

# Register your models here.
from .models import Employee, Order, OrderItem, Product


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order_employee",
        "order",
        "quantity",
    )

    def order_employee(self, obj):
        return (
            obj.product.name_product,
            obj.order.employee.first_name,
        )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name_product",
        "price",
    )

    list_display_links = (
        "name_product",
        "price",
    )

