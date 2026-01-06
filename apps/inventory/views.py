from django.shortcuts import render, redirect
from .models import Equipment, Maintenance
from .forms import EquipmentForm

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

def suppliers(request):
    return render(request, 'inventory/suppliers.html')

def all_equipment(request):
    equipments = Equipment.objects.all()
    return render(request, 'inventory/all_equipment.html', {'equipments': equipments})

def add_edit_equipment(request, id=None):
    if id:
        equipment = Equipment.objects.get(id=id)
        form = EquipmentForm(request.POST or None, instance=equipment)
    else:
        form = EquipmentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('inventory:all_equipment')

    return render(request, 'inventory/add_edit_equipment.html', {'form': form})

def maintenance_log(request):
    maintenances = Maintenance.objects.all()
    return render(request, 'inventory/maintenance_log.html', {'maintenances': maintenances})