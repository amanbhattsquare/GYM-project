from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('all-items/', views.all_items, name='all_items'),
    path('add-edit-item/', views.add_edit_item, name='add_edit_item'),
    path('stock-in/', views.stock_in, name='stock_in'),
    path('stock-out/', views.stock_out, name='stock_out'),
    path('low-stock/', views.low_stock, name='low_stock'),
    path('expiring-soon/', views.expiring_soon, name='expiring_soon'),
    path('suppliers/', views.suppliers, name='suppliers'),
]