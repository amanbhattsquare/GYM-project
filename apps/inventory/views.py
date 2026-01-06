from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, StockLog, Equipment, Maintenance
from .forms import ItemForm, StockOutForm, EquipmentForm, MaintenanceForm
from django.contrib import messages
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required

@login_required
def inventory_dashboard(request):
    gym = getattr(request, 'gym', None)
    return render(request, 'inventory/inventory_dashboard.html', {'gym': gym})

@login_required
def all_items(request):
    gym = getattr(request, 'gym', None)
    query = request.GET.get('q')
    category = request.GET.get('category')
    supplier = request.GET.get('supplier')
    stock_status = request.GET.get('status')

    items = Item.objects.filter(gym=gym, is_deleted=False)

    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query)
        )
    
    if category:
        items = items.filter(category__iexact=category)
    
    if supplier:
        items = items.filter(supplier__iexact=supplier)

    if stock_status:
        if stock_status == 'in_stock':
            items = items.filter(current_stock__gt=F('reorder_level'))
        elif stock_status == 'low_stock':
            items = items.filter(current_stock__lte=F('reorder_level'), current_stock__gt=0)
        elif stock_status == 'out_of_stock':
            items = items.filter(current_stock=0)

    context = {
        'items': items,
        'categories': Item.objects.filter(gym=gym).values_list('category', flat=True).distinct(),
        'suppliers': Item.objects.filter(gym=gym).values_list('supplier', flat=True).distinct(),
        'gym': gym,
    }
    return render(request, 'inventory/all_items.html', context)

@login_required
def add_edit_item(request, id=None):
    gym = getattr(request, 'gym', None)
    if id:
        item = get_object_or_404(Item, id=id, gym=gym)
        form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    else:
        form = ItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.added_by = request.user
            instance.gym = gym
            instance.save()
            messages.success(request, 'Item saved successfully!')
            return redirect('inventory:all_items')
        else:
            messages.error(request, 'Please correct the errors below.')

    item_suppliers = Item.objects.filter(gym=gym).values_list('supplier', flat=True).distinct()
    equipment_suppliers = Equipment.objects.filter(gym=gym).values_list('supplier', flat=True).distinct()
    suppliers = sorted([s for s in set(list(item_suppliers) + list(equipment_suppliers)) if s])

    categories = Item.objects.filter(gym=gym).values_list('category', flat=True).distinct()

    context = {
        'form': form,
        'suppliers': suppliers,
        'categories': categories,
        'gym': gym,
    }
    return render(request, 'inventory/add_inventory_item.html', context)

def _get_suppliers(gym):
    item_suppliers = Item.objects.filter(gym=gym).values_list('supplier', flat=True).distinct()
    equipment_suppliers = Equipment.objects.filter(gym=gym).values_list('supplier', flat=True).distinct()
    suppliers = sorted([s for s in set(list(item_suppliers) + list(equipment_suppliers)) if s])
    return suppliers

@login_required
def stock_out_view(request, item_id=None):
    gym = getattr(request, 'gym', None)
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            stock_log = form.save(commit=False)
            stock_log.transaction_type = 'stock_out'
            stock_log.added_by = request.user
            stock_log.gym = gym
            
            item = stock_log.item
            if item.current_stock < stock_log.quantity:
                messages.error(request, f'Not enough stock for {item.name}.')
                return redirect('inventory:stock_out')

            item.current_stock -= stock_log.quantity
            item.save()
            
            stock_log.save()
            
            messages.success(request, f'{item.name} has been stocked out successfully.')
            return redirect('inventory:stock_log', item_id=item.id)
    else:
        initial_data = {}
        if item_id:
            initial_data['item'] = get_object_or_404(Item, id=item_id, gym=gym)
        form = StockOutForm(initial=initial_data)
    
    context = {
        'form': form,
        'suppliers': _get_suppliers(gym),
        'gym': gym,
    }
    return render(request, 'inventory/stock_out.html', context)

@login_required
def stock_log_view(request, item_id):
    gym = getattr(request, 'gym', None)
    item = get_object_or_404(Item, id=item_id, gym=gym)
    logs = StockLog.objects.filter(item=item).order_by('-date')
    context = {
        'item': item,
        'logs': logs,
        'gym': gym,
    }
    return render(request, 'inventory/stock_log.html', context)

@login_required
def all_equipment(request):
    gym = getattr(request, 'gym', None)
    query = request.GET.get('q')
    category = request.GET.get('category')
    status = request.GET.get('status')

    equipments = Equipment.objects.filter(gym=gym, is_deleted=False)

    if query:
        equipments = equipments.filter(
            Q(name__icontains=query) |
            Q(serial_number__icontains=query)
        )
    
    if category:
        equipments = equipments.filter(category__iexact=category)

    if status:
        equipments = equipments.filter(status__iexact=status)

    context = {
        'equipments': equipments,
        'categories': Equipment.objects.filter(gym=gym).values_list('category', flat=True).distinct(),
        'gym': gym,
    }
    return render(request, 'inventory/all_equipment.html', context)

@login_required
def add_edit_equipment(request, id=None):
    gym = getattr(request, 'gym', None)
    if id:
        equipment = get_object_or_404(Equipment, id=id, gym=gym)
        form = EquipmentForm(request.POST or None, request.FILES or None, instance=equipment)
    else:
        form = EquipmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.added_by = request.user
            instance.gym = gym
            instance.save()
            messages.success(request, 'Equipment saved successfully!')
            return redirect('inventory:all_equipment')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    categories = Item.objects.filter(gym=gym).values_list('category', flat=True).distinct()

    context = {
        'form': form,
        'suppliers': _get_suppliers(gym),
        'categories': categories,
        'gym': gym,
    }
    return render(request, 'inventory/add_equipment.html', context)

@login_required
def maintenance_log(request):
    gym = getattr(request, 'gym', None)
    form = MaintenanceForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.added_by = request.user
            maintenance.gym = gym
            maintenance.save()
            messages.success(request, 'Maintenance log added successfully!')
            return redirect('inventory:maintenance_log')

    logs = Maintenance.objects.filter(gym=gym).order_by('-service_date')
    context = {
        'form': form,
        'logs': logs,
        'gym': gym,
    }
    return render(request, 'inventory/maintenance_log.html', context)