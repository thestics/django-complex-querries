from django.test import TestCase

# Create your tests here.

qs = Reservation.objects.annotate(
    last=models.Subquery(
        Reservation.objects
            .filter(rental__pk=models.OuterRef('rental__pk'), checkin__lt=models.OuterRef('checkin'))
            .order_by('-checkin')
            .values('pk')[:1]
    )
)