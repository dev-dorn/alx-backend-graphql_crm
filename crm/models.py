from django.db import models

# Create your models here.
from django.utils import timezone

class Customer(models.Model):
    name= models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    phone= models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class Order(models.Models):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id}"