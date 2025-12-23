import json
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, Count
from apps.billing.models import Payment
from apps.expenses.models import Expense
from apps.members.models import MembershipHistory, PersonalTrainer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from apps.superadmin.models import GymAdmin
from django.core.paginator import Paginator

@login_required
def business_report(request):
    try:
        gym_admin = GymAdmin.objects.get(user=request.user)
        gym = gym_admin.gym
    except GymAdmin.DoesNotExist:
        return render(request, 'error.html', {'message': 'Gym admin not found.'})

    # Time-based filters
    today = timezone.now().date()
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    try:
        start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today.replace(day=1)
        end_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
        end_date = today

    # KPI Calculations
    total_income = Payment.objects.filter(member__gym=gym, payment_date__date__range=[start_date, end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(gym=gym, date__range=[start_date, end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
    gross_income = total_income - total_expense

    membership_dues = MembershipHistory.objects.filter(member__gym=gym).annotate(due=F('total_amount') - F('paid_amount')).aggregate(total_due=Sum('due'))['total_due'] or 0
    pt_dues = PersonalTrainer.objects.filter(member__gym=gym).annotate(due=F('total_amount') - F('paid_amount')).aggregate(total_due=Sum('due'))['total_due'] or 0
    total_due = membership_dues + pt_dues

    # Fetching latest transactions for the tables
    latest_invoices = MembershipHistory.objects.filter(member__gym=gym, membership_start_date__range=[start_date, end_date]).order_by('-membership_start_date')
    latest_expenses = Expense.objects.filter(gym=gym, date__range=[start_date, end_date]).order_by('-date')[:10]
    latest_payments = Payment.objects.filter(member__gym=gym, payment_date__date__range=[start_date, end_date]).order_by('-payment_date')

    transactions = []
    for invoice in latest_invoices:
        is_new_registration = not MembershipHistory.objects.filter(member=invoice.member, pk__lt=invoice.pk).exists()
        transactions.append({
            'invoice': invoice,
            'profile': invoice.member.profile_picture.url if invoice.member.profile_picture else None,
            'member': invoice.member,
            'amount': invoice.total_amount,  # Total amount for this specific invoice
            'paid': invoice.paid_amount,  # Total paid for this invoice
            'due': invoice.due_amount,  # Due amount for this invoice
            'status': 'Paid' if invoice.due_amount <= 0 else 'Pending',
            'mode': invoice.payment_mode,
            'type': 'New' if is_new_registration else 'Subscription',
            'date': invoice.membership_start_date,
        })

    for payment in latest_payments:
        # This logic assumes that a payment without a related invoice is a due payment.
        if not MembershipHistory.objects.filter(member=payment.member, membership_start_date=payment.payment_date.date()).exists():
            member = payment.member

            # Calculate total due for the member AFTER the payment has been applied
            membership_due = member.membership_history.filter(status='active', gym=gym).aggregate(
                total=Sum(F('total_amount') - F('paid_amount'))
            )['total'] or 0

            pt_due = member.personal_trainer.filter(status='active', gym=gym).aggregate(
                total=Sum(F('total_amount') - F('paid_amount'))
            )['total'] or 0
            
            total_due_after = membership_due + pt_due
            
            # Calculate total due BEFORE the payment
            total_due_before = total_due_after + payment.amount

            transactions.append({
                'invoice': None,
                'profile': member.profile_picture.url if member.profile_picture else None,
                'member': member,
                'amount': total_due_before,  # Member's total due before this payment
                'paid': payment.amount,      # The actual amount paid now
                'due': total_due_after,       # Member's total due after this payment
                'status': 'Completed',
                'mode': payment.payment_mode,
                'type': 'Due',
                'date': payment.payment_date.date(),
            })
    
    transactions.sort(key=lambda item: item['date'], reverse=True)

    # Paginate the transactions
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    latest_transactions = paginator.get_page(page_number)

    # Chart Data: Income vs. Expense for the last 6 months
    labels = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):
        month = today - relativedelta(months=i)
        month_start = month.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

        labels.append(month.strftime("%b %Y"))

        monthly_income = Payment.objects.filter(member__gym=gym, payment_date__range=[month_start, month_end]).aggregate(Sum('amount'))['amount__sum'] or 0
        income_data.append(float(monthly_income))

        monthly_expense = Expense.objects.filter(gym=gym, date__range=[month_start, month_end]).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_data.append(float(monthly_expense))

    # Chart Data: Expense breakdown for the current month
    expense_breakdown = (
        Expense.objects.filter(gym=gym, date__range=[start_date, end_date])
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    expense_categories = [item['category'] for item in expense_breakdown]
    expense_amounts = [float(item['total'] or 0) for item in expense_breakdown]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'gross_income': gross_income,
        'total_due': total_due,
        'latest_transactions': latest_transactions,
        'latest_expenses': latest_expenses,
        'line_chart_labels': json.dumps(labels),
        'line_chart_income_data': json.dumps(income_data),
        'line_chart_expense_data': json.dumps(expense_data),
        'pie_chart_labels': json.dumps(expense_categories),
        'pie_chart_data': json.dumps(expense_amounts),
    }
    return render(request, 'business_report/business_report.html', context)