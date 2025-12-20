from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import RegisterForm, LoginForm
from .models import Employee, Product, Order, OrderItem


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

def add_to_cart(request):
    """Добавляем в корзину товар и количество"""
    if request.method == "POST":

        #Сначала получаем данные товара
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 0))

        #Проверка пользователя, чтоб он был
        employee_id = request.session.get("employee_id")
        if not employee_id:
            messages.error(request, "Войдите в аккаунт")
            return redirect("login")

        #Получаем объекты
        employee = get_object_or_404(Employee, id=employee_id)
        product = get_object_or_404(Product, id=product_id)

        #Находим или создаем заказ в Order
        order, created = Order.objects.get_or_create(
            employee=employee,
            status="Оформлен",
            dafaults={"order_data": timezone.now()}
        )

        #Находим или создаем OrderItem связь количества товара, который мы добавили в заказ Order
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product_id,
            defaults={"quantity": quantity}
        )

        if not created:
            #Если уже есть в корзине, просто обновляем количество
            order_item.quantity = quantity
            order_item.save()

        messages.success(request, f"Товар,{product.name_product}, добавлен в корзину! ")

        return redirect("start_page")

    return redirect("start_page")


def ordering(request):
    """Показываем корзину"""
    employee_id = request.session.get("employee_id")

    if not employee_id:
        return redirect("login")

    #Получаем объект сотрудника для шаблона
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "GET":
        #Показываем корзину
        try:
            # Находим корзину (order со статусом в корзине)
            order = Order.objects.get(
                employee_id=employee_id,
                status='cart'
            )
            # Получаем все товары через related_name=items
            order_items = order.items.all()

        except Order.DoesNotExist:
            # Корзины нет, создаем пустую
            order = None
            order_items = []

        context = {
            "order": order,
            "order_items": order_items,
            "employee": employee,
        }

        return render(request, "store_app/order.html", context)

    elif request.method == "POST":
        # Оформляем заказ, с изменением статуса, с cart на ordered
        try:
            # Находим корзину пользователя
            order = Order.objects.get(
                employee_id=employee_id,
                status='cart'
            )

            # Проверяем, что в корзине есть товар
            if not order.items.exists():
                messages.error(request, "Корзина пуста")
                return redirect("start_page")

            # Меняем статус с корзины cart на ordered
            order.status = "ordered"
            order.save()

            messages.success(
                request,
                f"✅ Заказ #{order.id} оформлен! Сумма: {order.total_price} ₽"
            )

        except Order.DoesNotExist:
            messages.error(request, "Корзина не найдена!")
            return redirect("start_page")


def personal_account(request):
    """Данные о себе"""
    employee_id = request.session.get("employee_id")

    if not employee_id:
        return redirect("login")

    employee = Employee.objects.get(id=employee_id)

    return render(
        request,
        "store_app/personal_account.html",
        {"employee": employee},
    )


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
