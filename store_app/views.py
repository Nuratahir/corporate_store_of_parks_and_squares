import json

from django.http import JsonResponse
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import RegisterForm, LoginForm
from .models import Employee, Product, Order, OrderItem, ChatMessage


def start_page(request):
    employee_id = request.session.get("employee_id")
    employee = None

    if employee_id:
        employee = Employee.objects.get(id=employee_id)

    products = Product.objects.all()

    context = {
        "employee": employee,
        "products": products,
    }

    return render(
        request,
        "store_app/start_page.html",
        context=context,
    )


def update_quantity(request, item_id):
    """Обновление количества товара в корзине"""
    if request.method == "POST":
        try:
            delta = int(request.POST.get("delta", 0))
            item = get_object_or_404(OrderItem, id=item_id)

            new_quantity = item.quantity + delta
            if new_quantity > 0:
                item.quantity = new_quantity
                item.save()
            else:
                item.delete()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


def remove_item(request, item_id):
    """Удаление товара из корзины"""
    if request.method == "POST":
        try:
            item = get_object_or_404(OrderItem, id=item_id)
            item.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


def add_all_to_cart(request):
    """Добавляет ВСЕ выбранные товары в корзину"""
    if request.method == "POST":
        employee_id = request.session.get("employee_id")

        if not employee_id:
            messages.error(request, "Войдите в аккаунт")
            return redirect("login")

        employee = get_object_or_404(Employee, id=employee_id)

        # Находим или создаем корзину
        order, _ = Order.objects.get_or_create(
            employee=employee, status="cart", defaults={"order_date": timezone.now()}
        )

        added_items = []

        # Получаем все данные POST
        for key, value in request.POST.items():
            if key.startswith("product_") and value.isdigit():
                product_id = key.replace("product_", "")
                quantity = int(value)

                if quantity > 0:
                    try:
                        product = Product.objects.get(id=product_id)

                        order_item, created = OrderItem.objects.get_or_create(
                            order=order,
                            product=product,
                            defaults={"quantity": quantity},
                        )

                        if not created:
                            order_item.quantity += quantity
                            order_item.save()
                            added_items.append(
                                f"✓ {product.name_product}: +{quantity} шт. (теперь {order_item.quantity})"
                            )
                        else:
                            added_items.append(
                                f"✓ {product.name_product}: {quantity} шт."
                            )

                    except Product.DoesNotExist:
                        continue

        # Показываем сообщение
        if added_items:
            messages.success(
                request,
                f"Добавлено в корзину:<br>"
                + "<br>".join(added_items[:5])
                + ("<br>...и другие" if len(added_items) > 5 else ""),
            )
        else:
            messages.warning(request, "Не выбрано ни одного товара!")

    return redirect("start_page")


def ordering(request):
    """Показываем корзину"""
    employee_id = request.session.get("employee_id")

    if not employee_id:
        return redirect("login")

    # Получаем объект сотрудника
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "GET":
        # Показываем корзину
        try:
            # Находим корзину (order со статусом в корзине)
            order = Order.objects.get(employee_id=employee_id, status="cart")
            # Получаем все товары через related_name=items
            order_items = order.items.all()

        except Order.DoesNotExist:
            # Корзины нет, создаем пустую
            order = None
            order_items = []

        # Получаем список ВСЕХ сотрудников (кроме текущего)
        all_employees = Employee.objects.exclude(id=employee_id).order_by(
            "first_name", "last_name"
        )

        context = {
            "order": order,
            "order_items": order_items,
            "employee": employee,
            "all_employees": all_employees,
        }

        return render(request, "store_app/ordering.html", context)

    elif request.method == "POST":
        # Оформляем заказ, с изменением статуса, с cart на ordered
        try:
            # Находим корзину пользователя
            order = Order.objects.get(employee_id=employee_id, status="cart")

            # Проверяем, что в корзине есть товар
            if not order.items.exists():
                messages.error(request, "Корзина пуста")
                return redirect("start_page")

            # Определяем получателя
            recipient_type = request.POST.get("recipient_type", "self")
            selected_email = request.POST.get("for_whom", "").strip()

            recipient_msg = "для себя"

            if recipient_type == "colleague" and selected_email:
                # Для коллеги
                order.for_whom = selected_email

            else:
                # Для себя
                order.for_whom = ""
                recipient_msg = "для себя"

            # Меняем статус с корзины cart на ordered
            order.status = "ordered"
            order.save()

            messages.success(
                request,
                f"Заказ #{order.id} оформлен {recipient_msg}! Сумма: {order.total_price} ₽",
            )

            return redirect("personal_account")

        except Order.DoesNotExist:
            messages.error(request, "Корзина не найдена!")
            return redirect("start_page")


def personal_account(request):
    """Данные о себе"""
    employee_id = request.session.get("employee_id")

    if not employee_id:
        return redirect("login")

    employee = Employee.objects.get(id=employee_id)

    # Получаем ВСЕ заказы сотрудника, кроме корзин (только оформленные заказы)
    orders = Order.objects.filter(
        employee=employee,
        status=Order.STATUS_ORDERED,  # только оформленные заказы
    ).order_by("-order_date")

    # получение чата сотрудника
    chat_messages = ChatMessage.objects.filter(employee=employee).order_by("timestamp")

    return render(
        request,
        "store_app/personal_account.html",
        {
            "employee": employee,
            "orders": orders,
            "chat_messages": chat_messages,
        },
    )


def send_message(request):
    """Обработка отправки сообщения от сотрудника"""
    if request.method == "POST":
        employee_id = request.session.get("employee_id")

        if employee_id:
            message_text = request.POST.get("message", "").strip()

            if message_text:
                employee = Employee.objects.get(id=employee_id)

                # Сохраняем сообщение в БД
                ChatMessage.objects.create(
                    employee=employee,
                    message_from_user=message_text,
                    message_to_admin=None,
                    timestamp=timezone.now(),
                )

    return redirect("personal_account")


def logout(request):
    request.session.pop("employee_id", None)
    return redirect("login")


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            employee = Employee.objects.filter(
                email=email,
                password=password,
            ).first()

            if employee:
                request.session["employee_id"] = employee.id
                return redirect("personal_account")
            else:
                form.add_error(None, "Неверный пароль или Email")

    else:
        form = LoginForm()

    return render(request, "store_app/login.html", {"form": form})


def registration(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            Employee.objects.create(
                first_name=form.cleaned_data.get("first_name"),
                last_name=form.cleaned_data.get("last_name"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
                position=form.cleaned_data.get("position"),
                department=form.cleaned_data.get("department"),
            )
            return redirect("login")
    else:
        form = RegisterForm()

    context = {"form": form}
    return render(request, "store_app/registration.html", context=context)
