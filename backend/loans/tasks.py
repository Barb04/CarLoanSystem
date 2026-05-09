from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Loan

@shared_task
def check_overdue_loans():
    """Run every hour — detect overdue loans and charge fees."""
    now = timezone.now()
    overdue_loans = Loan.objects.filter(
        expected_return_date__lt=now,
        actual_return_date__isnull=True,
        status='active'
    )
    
    for loan in overdue_loans:
        loan.status = 'overdue'
        fee = loan.calculate_extension_fee()
        loan.extension_fee = fee
        loan.calculate_total()
        loan.save()
        
        # Send email notification
        send_overdue_notification.delay(loan.id, fee)
    
    return f"Processed {overdue_loans.count()} overdue loans."

@shared_task
def send_overdue_notification(loan_id, current_fee):
    loan = Loan.objects.get(id=loan_id)
    send_mail(
        subject=f'⚠️ Overdue Alert — Car Return Required',
        message=f"""
        Dear {loan.borrower.get_full_name()},
        
        Your rental of {loan.car} was due on {loan.expected_return_date.strftime('%d %b %Y at %H:%M')}.
        
        Current late fee accumulated: ${current_fee:.2f}
        This fee increases every hour you delay.
        
        Please return the vehicle immediately to avoid further charges.
        
        FleetGuard System
        """,
        from_email='noreply@fleetguard.com',
        recipient_list=[loan.borrower.email],
    )