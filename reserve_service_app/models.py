from django.db import models


class Rental(models.Model):
    name = models.CharField(max_length=256)


class Reservation(models.Model):
    rental = models.ForeignKey(
        Rental, on_delete=models.CASCADE, related_name='reservations')
    checkin = models.DateTimeField()
    checkout = models.DateTimeField()
