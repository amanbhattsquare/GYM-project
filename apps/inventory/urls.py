from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('all-items/', views.all_items, name='all_items'),
    path('add-edit-item/', views.add_edit_item, name='add_edit_item'),
    path('stock-in/', views.stock_in, name='stock_in'),
    path('stock-out/', views.stock_out, name='stock_out'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('all-equipment/', views.all_equipment, name='all_equipment'),
    path('add-edit-equipment/', views.add_edit_equipment, name='add_edit_equipment'),
    path('add-edit-equipment/<int:id>/', views.add_edit_equipment, name='add_edit_equipment'),
    path('maintenance-log/', views.maintenance_log, name='maintenance_log'),
]