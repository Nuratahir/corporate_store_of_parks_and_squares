from django.contrib import admin

# Register your models here.
from .models import Employee, Order, OrderItem, Product, ChatMessage


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


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "message_from_user_preview",
        "message_to_admin_preview",
        "timestamp",
    )
    list_filter = ("employee", "timestamp")

    def message_from_user_preview(self, obj):
        return obj.message_from_user[:50] + "..." if obj.message_from_user else "-"

    message_from_user_preview.short_description = "Вопрос от сотрудника"

    def message_to_admin_preview(self, obj):
        return obj.message_to_admin[:50] + "..." if obj.message_to_admin else "-"

    message_to_admin_preview.short_description = "Ответ админа"
