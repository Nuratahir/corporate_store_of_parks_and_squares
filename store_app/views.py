from itertools import product

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
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


def ordering(request):
    return render(request, "store_app/ordering.html")


def personal_account(request):
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
