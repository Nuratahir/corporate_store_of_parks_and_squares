from django.utils import timezone
from django.db import models
from django.core.validators import MinLengthValidator


class Employee(models.Model):
    """Сотрудник"""

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, unique=True)
    department = models.CharField(max_length=30)
    position = models.CharField(max_length=30)
    # у orders, уже есть связь в нужном классе
    password = models.TextField(validators=[MinLengthValidator(8)])

    def __str__(self):
        return f"{self.first_name, self.last_name, self.email}"


class Product(models.Model):
    """Товар"""

    name_product = models.CharField(max_length=30)
    price = models.FloatField()

    def __str__(self):
        return f"{self.name_product}: \n{self.price}"


class Order(models.Model):
    """Заказ"""

    # Статусы заказа
    STATUS_CART = "cart"
    STATUS_ORDERED = "ordered"
    STATUS_CHOICES = [
        (STATUS_CART, "Корзина"),
        (STATUS_ORDERED, "Оформлен"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    order_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CART,
    )
    # добавлен столбец, для кого
    for_whom = models.EmailField(
        max_length=254,
        default="",
    )

    def __str__(self):
        return f"Order #{self.id} by {self.employee.first_name}"

    @property
    def total_price(self):
        """Сумма всех товаров в заказе"""
        total = 0
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total


class OrderItem(models.Model):
    """Связь между заказом и товаром. Позиция в заказе: товар + количество"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField()

    @property
    def item_total(self):
        """Сумма за эту позицию (цена × количество)"""
        if self.product.price:
            return self.product.price * self.quantity
        return 0

    def __str__(self):
        return f"{self.product.name_product} * {self.quantity}"
