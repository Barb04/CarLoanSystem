from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Loan, Pledge
from .serializers import LoanCreateSerializer, LoanDetailSerializer, PledgeSerializer
from fleet.models import Car
from damage.models import AuditLog

class LoanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'super_admin']:
            return Loan.objects.all().select_related('borrower', 'car', 'pledge')
        return Loan.objects.filter(borrower=user).select_related('car')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LoanCreateSerializer
        return LoanDetailSerializer
    
    def perform_create(self, serializer):
        car = serializer.validated_data['car']
        user = self.request.user
        start = serializer.validated_data['start_date']
        end = serializer.validated_data['expected_return_date']
        days = max(1, (end - start).days)
        base = float(car.daily_rate) * days
        deposit = car.get_deposit_amount(user)
        
        loan = serializer.save(
            borrower=user,
            daily_rate=car.daily_rate,
            total_days=days,
            base_amount=base,
            deposit_amount=deposit,
            total_amount_due=base + deposit,
        )
        # Mark car as unavailable
        car.status = 'on_loan'
        car.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify_pledge(self, request, pk=None):
        """Admin verifies the pledge and releases pickup code."""
        loan = self.get_object()
        if loan.pledge and loan.pledge.status != 'verified':
            loan.pledge.status = 'verified'
            loan.pledge.verified_by = request.user
            loan.pledge.verified_at = timezone.now()
            loan.pledge.save()
            loan.status = 'pledge_verified'
            loan.save()
            # Log it
            AuditLog.objects.create(
                action='pledge_verified',
                performed_by=request.user,
                target_loan=loan,
                description=f"Pledge verified for loan {loan.loan_id}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            return Response({'message': 'Pledge verified. Pickup code released.', 'pickup_code': loan.pickup_code})
        return Response({'error': 'Pledge already verified or not found.'}, status=400)

    @action(detail=True, methods=['post'])
    def confirm_return(self, request, pk=None):
        """Mark car as returned and trigger damage inspection."""
        loan = self.get_object()
        loan.actual_return_date = timezone.now()
        loan.status = 'returned'
        loan.car.status = 'pending_inspection'
        loan.car.save()
        loan.calculate_total()
        loan.save()
        # Update user stats
        user = loan.borrower
        user.total_loans += 1
        if loan.is_overdue():
            user.late_returns += 1
        user.calculate_trust_score()
        return Response({'message': 'Return confirmed. Please complete damage inspection.'})