from django.db import models
from django.db.models import Q, Window, Case, When
from django.db.models.functions import Lag

from reserve_service_app.models import Reservation, Rental
from reserve_service_app.serialization import \
    ReservationStatus, ReservationStatusBase


def get_reservation_summary__subquery():
    # Get reservation stat with one query.
    # M = len(Rentals)
    # N = len(Reservations)
    # Assume each rental has K reservations
    # K < M < N
    # Complexity: O(MN^2 K logK)
    # (Not accounting for possible query optimizations from database)
    qs = Reservation.objects.select_related('rental') \
        .annotate(
            last=models.Subquery(
                Reservation.objects
                    .filter(rental__pk=models.OuterRef('rental__pk'),
                            checkin__lt=models.OuterRef('checkin'))
                    .order_by('-checkin')
                    .values('pk')[:1]
            )
        )
    return ReservationStatus(qs, many=True).data


def get_reservation_summary__post_proc():
    # Get reservation stat with several queries + python post-processing
    # M = len(Rentals)
    # N = len(Reservations)
    # K < M < N
    # Assume each rental has K reservations
    # Complexity: O(MN K logK)
    #
    # Shape of final data suggests, that to build 'prev_id' column we can avoid
    # per-row calculations. Instead, we can sort reservations by time
    # (thus, ensuring that each following reservation came after previous one)
    # take 'pk' column for each 'rental_id' section and rotate it
    # downwards.
    # i.e.
    # | reserve_name | rental_pk | checkin   | checkout
    # | rental-1     | pk-1      | checkin-1 | checkout-1
    # | rental-1     | pk-2      | checkin-2 | checkout-2
    # | rental-1     | pk-3      | checkin-3 | checkout-3
    #
    # becomes
    # | reserve_name | rental_pk | checkin   | checkout
    # | rental-1     | pk-1      | checkin-1 | checkout-1 |
    # | rental-1     | pk-2      | checkin-2 | checkout-2 | pk-1
    # | rental-1     | pk-3      | checkin-3 | checkout-3 | pk-2
    #
    # (we took column 'rental_pk', "rotated it downwards" and joined
    #
    # Great, now we got rid out sub-queries per joined row. However, now we
    # execute transaction per each rental, thus driving time complexity up as
    # data grows
    res = []
    rentals = Rental.objects\
        .prefetch_related('reservations')\
        .order_by('pk')\
        .all()
    for rental in rentals:
        prev_pks = [
            {'pk': None},
            *list(rental.reservations.order_by('checkin').values('pk'))[:-1]
        ]
        for reservation, prev_res in zip(rental.reservations.all(), prev_pks):
            data = ReservationStatusBase(reservation).data
            data['prev_reservation_id'] = prev_res['pk']
            res.append(data)
    return res


def get_reservation_summary__lag():
    # One query but with window function now
    # M = len(Rentals)
    # N = len(Reservations)
    # Assume each rental has K reservations
    # K < M < N
    # Complexity: O(MN K logK)
    #
    # Now we take best from the both worlds: one sql query with same "rotating"
    # idea as previously. Thus achieving linear time complexity with respect
    # to the Reservation size.
    # We achieve this in particular using window functions and noticing, that
    # we really need to know how previous and current row looks to determine
    # value of current 'previous_id' column
    #
    # with 4.7mb sqlite database timings for three approaches are:
    # 5.32450795173645
    # 3.6718690395355225
    # 2.1188364028930664
    # Asymptotically, similar pattern holds
    qs = Reservation.objects.select_related('rental') \
        .order_by('rental__pk', 'checkin') \
        .annotate(
        last=Case(
            When(
                Q(rental__name=Window(expression=Lag('rental__name'))),
                then=Window(expression=Lag('pk'))
            )
        )
    )
    return ReservationStatus(qs, many=True).data