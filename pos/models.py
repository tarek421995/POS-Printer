from django.db import models


class Sequence(models.Model):
    number = models.IntegerField(default=0)

class PrinterPreference(models.Model):
    device_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, unique=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.device_name} - Default: {self.is_default}"
    