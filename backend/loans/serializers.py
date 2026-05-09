from rest_framework import serializers
from .models import Loan, Pledge
from fleet.models import Car
from django.utils import timezone

class PledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = '__all__'
        read_only_fields = ['user', 'status', 'verified_by', 'verified_at']

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['car', 'start_date', 'expected_return_date', 'notes']
    
    def validate(self, data):
        car = data['car']
        # Check car is available
        if not car.is_available():
            raise serializers.ValidationError(
                f"This car is currently {car.status} and cannot be booked."
            )
        # Check dates
        if data['start_date'] >= data['expected_return_date']:
            raise serializers.ValidationError("Return date must be after start date.")
        if data['start_date'] < timezone.now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return data

class LoanDetailSerializer(serializers.ModelSerializer):
    borrower_name = serializers.CharField(source='borrower.get_full_name', read_only=True)
    borrower_trust_score = serializers.IntegerField(source='borrower.trust_score', read_only=True)
    car_display = serializers.CharField(source='car.__str__', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    current_late_fee = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = '__all__'
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_current_late_fee(self, obj):
        return obj.calculate_extension_fee()