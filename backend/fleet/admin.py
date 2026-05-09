# fleet/admin.py
from django.contrib import admin
from .models import Car, CarCategory, CarPhoto

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'make', 'model', 'year', 'status', 'daily_rate']
    list_filter = ['status', 'category', 'fuel_type']
    search_fields = ['license_plate', 'make', 'model', 'vin_number']
    list_editable = ['status']