from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    face_scan = models.TextField(null=True, blank=True)
    emirates_id = models.CharField(max_length=50, unique=True,null=True,blank=True)
    passport = models.CharField(max_length=50, unique=True, null=True, blank=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('blocked', 'Blocked'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set', 
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class CardDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=16)
    expiry = models.CharField(max_length=5)
    cvv = models.CharField(max_length=4)
    cardholder_name = models.CharField(max_length=100)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
        ('transfer', 'Transfer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    card = models.ForeignKey(CardDetail, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    currency_from = models.CharField(max_length=10)
    currency_to = models.CharField(max_length=10)





class DeliveryLocation(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='delivery_locations')
    is_current_location = models.BooleanField(default=False)
    building_type = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()


class TransferTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('send_money', 'Send Money'),
        ('receive_money', 'Receive Money'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    card = models.ForeignKey(CardDetail, on_delete=models.CASCADE)
    amount_sent = models.DecimalField(max_digits=10, decimal_places=2)
    currency_sent = models.CharField(max_length=3)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    currency_received = models.CharField(max_length=3)
    message_to_recipient = models.TextField(blank=True, null=True)
    location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

class DeliverySchedule(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='delivery_schedules')
    delivery_type = models.CharField(max_length=50)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()


class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class DigitalSignature(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signature_data = models.TextField()