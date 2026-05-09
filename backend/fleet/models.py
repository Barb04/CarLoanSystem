from django.db import models
import uuid

class CarCategory(models.Model):
    name = models.CharField(max_length=100)  # Economy, SUV, Luxury
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Car(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('pending_inspection', 'Pending Inspection'),
    ]
    
    # Identity
    car_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    make = models.CharField(max_length=100)        # Toyota
    model = models.CharField(max_length=100)       # Camry
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20, unique=True)
    vin_number = models.CharField(max_length=50, unique=True)
    
    # Categorisation
    category = models.ForeignKey(CarCategory, on_delete=models.SET_NULL, null=True)
    
    # Financial
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    market_valuation = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_deposit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=30.00
    )
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='available')
    mileage = models.IntegerField(default=0)
    fuel_type = models.CharField(max_length=30, default='Petrol')
    transmission = models.CharField(max_length=20, default='Automatic')
    seat_capacity = models.IntegerField(default=5)
    
    # Media
    primary_photo = models.ImageField(upload_to='cars/primary/', null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available(self):
        return self.status == 'available'

    def get_deposit_amount(self, user):
        """Calculate required deposit based on user's trust tier."""
        tier_multipliers = {
            'GOLD': 0.15,
            'SILVER': 0.25,
            'BRONZE': 0.35,
            'HIGH_RISK': 0.50,
        }
        multiplier = tier_multipliers.get(user.get_tier(), 0.35)
        return round(float(self.market_valuation) * multiplier, 2)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} [{self.license_plate}]"

class CarPhoto(models.Model):
    """Multiple photos per car."""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='cars/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)