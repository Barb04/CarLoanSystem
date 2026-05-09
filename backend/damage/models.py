from django.db import models
from django.conf import settings

class DamageReport(models.Model):
    SEVERITY_CHOICES = [
        ('none', 'No Damage'),
        ('minor', 'Minor (Scratches/Dents)'),
        ('moderate', 'Moderate (Panel Damage)'),
        ('major', 'Major (Structural)'),
        ('total_loss', 'Total Loss'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('under_assessment', 'Under Assessment'),
        ('cost_determined', 'Cost Determined'),
        ('paid', 'Paid'),
        ('waived', 'Waived by Admin'),
        ('disputed', 'Disputed'),
    ]
    
    loan = models.ForeignKey('loans.Loan', on_delete=models.CASCADE, related_name='damage_reports')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='none')
    description = models.TextField()
    location_on_car = models.CharField(max_length=200)  # "Front bumper, left side"
    
    estimated_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='reported')
    
    # Who waived the fee (for audit log)
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='waived_damages'
    )
    waiver_reason = models.TextField(blank=True)
    
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class DamagePhoto(models.Model):
    """Before/After photos linked to a damage report."""
    PHOTO_TYPE_CHOICES = [
        ('before', 'Before Trip'),
        ('after', 'After Trip'),
        ('damage', 'Damage Close-up'),
    ]
    damage_report = models.ForeignKey(
        DamageReport, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to='damage/photos/')
    photo_type = models.CharField(max_length=10, choices=PHOTO_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    """Every important action is logged here to prevent fraud."""
    ACTION_CHOICES = [
        ('status_change', 'Status Changed'),
        ('fee_waived', 'Fee Waived'),
        ('pledge_verified', 'Pledge Verified'),
        ('car_released', 'Car Released'),
        ('damage_assessed', 'Damage Assessed'),
    ]
    
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    target_loan = models.ForeignKey(
        'loans.Loan', on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
