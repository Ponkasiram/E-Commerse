from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default="General")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=10)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class Order(models.Model):
    PAYMENT_CHOICES = [("COD", "Cash on delivery")]
    STATUS_CHOICES = [
        ("Pending", "Pending"), ("Processing", "Processing"),
        ("Shipped", "Shipped"), ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="COD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
