from django.contrib import admin
from .models import Loan, Pledge

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'borrower', 'car', 'status', 'start_date', 'expected_return_date']
    list_filter = ['status']
    search_fields = ['borrower__username', 'car__license_plate', 'pickup_code']

@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    list_display = ['pledge_id', 'user', 'pledge_type', 'status', 'estimated_value']
    list_filter = ['status', 'pledge_type']
    search_fields = ['user__username', 'asset_description']
