from .permissions import is_staff, is_client


def auth_groups(request):
    return {
        "is_staff": is_staff(request.user),
        "is_client": is_client(request.user),
        "search_query": request.GET.get("q", "").strip(),
    }
