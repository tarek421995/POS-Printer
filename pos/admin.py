from django.contrib import admin

from pos.models import PrinterPreference, Sequence

# Register your models here.
admin.site.register(PrinterPreference)
admin.site.register(Sequence)