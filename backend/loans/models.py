from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import random
import string

def generate_pickup_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Pledge(models.Model):
    """Collateral/Security Asset pledged by the borrower."""
    
    PLEDGE_TYPE_CHOICES = [
        ('title_deed', 'Property Title Deed'),
        ('logbook', 'Vehicle Logbook'),
        ('bank_guarantee', 'Bank Guarantee Letter'),
        ('other', 'Other Asset'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('verified', 'Verified & Accepted'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned to Owner'),
    ]
    
    pledge_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pledges'
    )
    
    pledge_type = models.CharField(max_length=30, choices=PLEDGE_TYPE_CHOICES)
    asset_description = models.TextField()
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Document uploads
    document_front = models.FileField(upload_to='pledges/documents/')
    document_back = models.FileField(upload_to='pledges/documents/', null=True, blank=True)
    supporting_document = models.FileField(upload_to='pledges/supporting/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_pledges'
    )
    verification_notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pledge by {self.user.username} - {self.get_pledge_type_display()}"

class Loan(models.Model):
    """The core loan/rental record."""
    
    STATUS_CHOICES = [
        ('pending_pledge', 'Awaiting Pledge Verification'),
        ('pledge_verified', 'Pledge Verified - Awaiting Pickup'),
        ('active', 'Active / Car Picked Up'),
        ('overdue', 'Overdue'),
        ('returned', 'Returned - Awaiting Inspection'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    loan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Relationships
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='loans'
    )
    car = models.ForeignKey('fleet.Car', on_delete=models.PROTECT, related_name='loans')
    pledge = models.OneToOneField(
        Pledge, on_delete=models.PROTECT, related_name='loan', null=True, blank=True
    )
    
    # Dates
    booking_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    # Financials
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_days = models.IntegerField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    extension_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    damage_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Pickup
    pickup_code = models.CharField(max_length=10, default=generate_pickup_code, unique=True)
    pickup_confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pickup_confirmations'
    )
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_pledge')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_overdue(self):
        if self.actual_return_date:
            return False
        return timezone.now() > self.expected_return_date

    def calculate_extension_fee(self):
        """Exponentially increasing late fee per hour."""
        if not self.is_overdue():
            return 0
        hours_late = (timezone.now() - self.expected_return_date).total_seconds() / 3600
        # Base hourly rate x exponential multiplier
        hourly_rate = float(self.daily_rate) / 24
        fee = 0
        for hour in range(int(hours_late)):
            multiplier = 1 + (hour * 0.1)   # Grows 10% each hour
            fee += hourly_rate * multiplier
        return round(fee, 2)

    def calculate_total(self):
        self.extension_fee = self.calculate_extension_fee()
        self.total_amount_due = (
            float(self.base_amount) +
            float(self.extension_fee) +
            float(self.damage_fee)
        )
        self.save()
        return self.total_amount_due

    def __str__(self):
        return f"Loan {self.loan_id} — {self.borrower.username} [{self.status}]"