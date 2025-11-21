from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('invoice/<int:member_id>/<int:history_id>/', views.invoice, name='invoice'),
    path('pt_invoice/<int:member_id>/<int:pt_invoice_id>/', views.pt_invoice, name='pt_invoice'),
    path('invoices/', views.invoices_list, name='invoices_list'),

    path('submit_due/', views.submit_due, name='submit_due'),
    path('payment_invoice/<int:payment_id>/', views.payment_invoice, name='payment_invoice'),
]