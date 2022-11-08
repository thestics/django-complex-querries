from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reserve_service_app.querries import get_reservation_summary__lag


@api_view(['GET'])
def reservation_summary(request):
    return Response(get_reservation_summary__lag(), status=status.HTTP_200_OK)
