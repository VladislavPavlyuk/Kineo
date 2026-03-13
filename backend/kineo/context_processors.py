from .permissions import is_staff, is_client
from .models import Booking


def auth_groups(request):
    user = request.user
    is_staff_flag = is_staff(user)
    is_client_flag = is_client(user)
    has_bookings = False
    if user.is_authenticated and is_client_flag:
        has_bookings = Booking.objects.filter(user=user).exists()
    return {
        "is_staff": is_staff_flag,
        "is_client": is_client_flag,
        "has_bookings": has_bookings,
        "search_query": request.GET.get("q", "").strip(),
    }
