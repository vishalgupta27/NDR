from django.db import models
from products.models import OrderDetails


# Create your models here.

class ExtendTransaction(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, null=True, blank=True)
    extendFromDate = models.DateTimeField(null=True, blank=True)
    extendToDate = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = (
        ('Requested', 'Requested'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    extendStatus = models.CharField(max_length=100, choices=STATUS_CHOICES, null=True, blank=True)
    extendPaymentId = models.CharField(max_length=100, null=True, blank=True)
    extendAmount = models.DecimalField(max_digits=10, decimal_places=2)
    extentPaymentStatus = models.BooleanField(default=False)
    extentCreatedAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'
