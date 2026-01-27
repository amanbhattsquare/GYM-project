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

    today = timezone.now().date()
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    try:
        start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today.replace(day=1)
        end_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
        end_date = today

    total_income = Payment.objects.filter(member__gym=gym, payment_date__date__range=[start_date, end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(gym=gym, date__range=[start_date, end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
    gross_income = total_income - total_expense

    membership_dues = MembershipHistory.objects.filter(member__gym=gym, status='active').aggregate(total_due=Sum(F('total_amount') - F('paid_amount')))['total_due'] or 0
    pt_dues = PersonalTrainer.objects.filter(member__gym=gym, status='active').aggregate(total_due=Sum(F('total_amount') - F('paid_amount')))['total_due'] or 0
    total_due = membership_dues + pt_dues

    payments = Payment.objects.filter(member__gym=gym, payment_date__date__range=[start_date, end_date]).select_related('member', 'membership_history', 'personal_trainer').order_by('-payment_date')
    
    transactions = []
    for p in payments:
        trans_type = "Due"
        invoice = p.membership_history or p.personal_trainer
        
        if p.personal_trainer:
            trans_type = "PT"
        elif p.membership_history:
            is_first_payment = p.membership_history.payments.order_by('payment_date').first().id == p.id
            if is_first_payment:
                is_first_ever = not MembershipHistory.objects.filter(member=p.member, pk__lt=p.membership_history.pk).exists()
                trans_type = "New" if is_first_ever else "Renewal"
        
        transactions.append({
            'date': p.payment_date.date(),
            'member': p.member,
            'invoice': invoice,
            'invoice_type': 'pt' if p.personal_trainer else 'membership' if p.membership_history else '',
            'amount': invoice.total_amount if invoice else p.amount,
            'paid': p.amount,
            'due': invoice.due_amount if invoice else 0,
            'status': 'Paid' if (invoice and invoice.due_amount <= 0) else 'Pending',
            'mode': p.payment_mode,
            'type': trans_type,
        })

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    latest_transactions = paginator.get_page(page_number)
    
    latest_expenses = Expense.objects.filter(gym=gym, date__range=[start_date, end_date]).order_by('-date')[:10]

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