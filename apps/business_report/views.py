import json
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, Count
from apps.billing.models import Payment
from apps.expenses.models import Expense
from apps.members.models import MembershipHistory, PersonalTrainer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def business_report(request):
    # Time-based filters
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    # KPI Calculations
    total_income = Payment.objects.filter(payment_date__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(date__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    gross_income = total_income - total_expense

    membership_dues = MembershipHistory.objects.annotate(due=F('total_amount') - F('paid_amount')).aggregate(total_due=Sum('due'))['total_due'] or 0
    pt_dues = PersonalTrainer.objects.annotate(due=F('total_amount') - F('paid_amount')).aggregate(total_due=Sum('due'))['total_due'] or 0
    total_due = membership_dues + pt_dues

    # Fetching latest transactions for the tables
    latest_invoices = MembershipHistory.objects.filter(membership_start_date__gte=this_month_start).order_by('-membership_start_date')[:10]
    latest_expenses = Expense.objects.filter(date__gte=this_month_start).order_by('-date')[:10]

    # Chart Data: Income vs. Expense for the last 6 months
    labels = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):
        month = today - relativedelta(months=i)
        month_start = month.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

        labels.append(month.strftime("%b %Y"))

        monthly_income = Payment.objects.filter(payment_date__range=[month_start, month_end]).aggregate(Sum('amount'))['amount__sum'] or 0
        income_data.append(float(monthly_income))

        monthly_expense = Expense.objects.filter(date__range=[month_start, month_end]).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_data.append(float(monthly_expense))

    # Chart Data: Expense breakdown for the current month
    expense_breakdown = (
        Expense.objects.filter(date__gte=this_month_start)
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
        'latest_invoices': latest_invoices,
        'latest_expenses': latest_expenses,
        'line_chart_labels': json.dumps(labels),
        'line_chart_income_data': json.dumps(income_data),
        'line_chart_expense_data': json.dumps(expense_data),
        'pie_chart_labels': json.dumps(expense_categories),
        'pie_chart_data': json.dumps(expense_amounts),
    }
    return render(request, 'business_report/business_report.html', context)