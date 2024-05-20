from django.urls import path
from .views import home, list_usb_devices, print_sequence, sequence_view



app_name = 'pos'

urlpatterns = [
    path('', home, name='home'),
    path('sequence_view', sequence_view, name='sequence_view'),
    path('list_usb_devices/', list_usb_devices, name='list_usb_devices'),]
