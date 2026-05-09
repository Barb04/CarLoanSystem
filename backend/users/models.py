from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Extended user with trust scoring and role management."""
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Trust & Risk System
    trust_score = models.IntegerField(default=50)  # 0–100
    total_loans = models.IntegerField(default=0)
    late_returns = models.IntegerField(default=0)
    damage_incidents = models.IntegerField(default=0)
    
    # Verification
    is_id_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_trust_score(self):
        """Recalculate trust score based on behaviour history."""
        base = 50
        # Reward on-time returns
        on_time = self.total_loans - self.late_returns
        base += on_time * 5
        # Penalise late returns and damage
        base -= self.late_returns * 10
        base -= self.damage_incidents * 15
        # Verification bonuses
        if self.is_id_verified:
            base += 10
        if self.is_email_verified:
            base += 5
        self.trust_score = max(0, min(100, base))
        self.save()
        return self.trust_score

    def get_tier(self):
        """Return risk tier based on trust score."""
        if self.trust_score >= 80:
            return 'GOLD'
        elif self.trust_score >= 60:
            return 'SILVER'
        elif self.trust_score >= 40:
            return 'BRONZE'
        else:
            return 'HIGH_RISK'

    def __str__(self):
        return f"{self.username} ({self.get_tier()})"