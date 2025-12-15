from django import forms
from django.core.validators import MinLengthValidator


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        label="Имя",
    )
    last_name = forms.CharField(
        max_length=30,
        label="Фамилия",
    )
    email = forms.EmailField(
        max_length=254,
        label="Email",
    )
    department = forms.CharField(
        max_length=30,
        label="Отдел",
    )
    position = forms.CharField(
        max_length=30,
        label="Должность",
    )
    password = forms.CharField(
        validators=[MinLengthValidator(8)],
        label="Пароль",
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
    )
    password = forms.CharField(
        label="Пароль",
    )
