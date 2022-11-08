from rest_framework import serializers


class ReservationStatusBase(serializers.Serializer):
    rental_name = serializers.CharField(source='rental.name')
    checkin = serializers.DateTimeField()
    checkout = serializers.DateTimeField()


class ReservationStatus(ReservationStatusBase):
    prev_reservation_id = serializers.IntegerField(source='last')
