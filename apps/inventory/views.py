from django.shortcuts import render

def inventory_dashboard(request):
    return render(request, 'inventory/dashboard.html')

def all_items(request):
    return render(request, 'inventory/all_items.html')

def add_edit_item(request):
    return render(request, 'inventory/add_edit_item.html')

def stock_in(request):
    return render(request, 'inventory/stock_in.html')

def stock_out(request):
    return render(request, 'inventory/stock_out.html')

def low_stock(request):
    return render(request, 'inventory/low_stock.html')

def expiring_soon(request):
    return render(request, 'inventory/expiring_soon.html')

def suppliers(request):
    return render(request, 'inventory/suppliers.html')


# Create your views here.