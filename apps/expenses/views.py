from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required

<<<<<<< HEAD
# LIST EXPENSES (not deleted)
=======

# ----------------------------
# LIST EXPENSES (not deleted)
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expenses(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    payment_mode = request.GET.get('payment_mode')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    expenses_list = Expense.objects.filter(is_deleted=False).order_by('-date')

    # SEARCH
    if query:
        expenses_list = expenses_list.filter(
            Q(category__icontains=query) |
            Q(description__icontains=query) |
            Q(vendor_name__icontains=query)
        )

    # FILTERS
    if category:
        expenses_list = expenses_list.filter(category=category)

    if payment_mode:
        expenses_list = expenses_list.filter(payment_mode=payment_mode)

    if date_from:
        expenses_list = expenses_list.filter(date__gte=date_from)

    if date_to:
        expenses_list = expenses_list.filter(date__lte=date_to)

    # PAGINATION
    paginator = Paginator(expenses_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'expenses/expenses.html', {
        'expenses': page_obj,
        'page_obj': page_obj,
        'categories': Expense.EXPENSE_CATEGORIES,
        'payment_modes': Expense.PAYMENT_MODES,
    })

<<<<<<< HEAD
# ADD EXPENSE
=======

# ----------------------------
# ADD EXPENSE
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user  # auto assign staff
            expense.save()
            return redirect('expenses')
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {'form': form})

<<<<<<< HEAD
# EDIT EXPENSE
=======

# ----------------------------
# EDIT EXPENSE
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, is_deleted=False)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expenses')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {'form': form})

<<<<<<< HEAD
# SOFT DELETE (Send to Trash)
=======

# ----------------------------
# SOFT DELETE (Send to Trash)
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.is_deleted = True
    expense.save()
    return redirect('expenses')

<<<<<<< HEAD
# APPROVE EXPENSE
@login_required
def expense_approve(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.approved_by = request.user
    expense.save()
    return redirect('expenses')


# TRASH PAGE
=======

# ----------------------------
# TRASH PAGE
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_trash(request):
    trash_list = Expense.objects.filter(is_deleted=True).order_by('-date')

    paginator = Paginator(trash_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'expenses/expense_trash.html', {
        'expenses': page_obj,
        'page_obj': page_obj,
    })

<<<<<<< HEAD
# RESTORE FROM TRASH
=======

# ----------------------------
# RESTORE FROM TRASH
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_restore(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.is_deleted = False
    expense.save()
    return redirect('expense_trash')

<<<<<<< HEAD
# PERMANENT DELETE
=======

# ----------------------------
# PERMANENT DELETE
# ----------------------------
>>>>>>> 62d6936db457b1b92c4574af858d4e2c5465788d
@login_required
def expense_delete_permanent(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('expense_trash')