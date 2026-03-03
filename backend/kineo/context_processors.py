def auth_groups(request):
    is_staff = False
    is_client = False
    if request.user.is_authenticated:
        group_names = set(request.user.groups.values_list("name", flat=True))
        is_staff = "Staff" in group_names
        is_client = "Clients" in group_names
    return {"is_staff": is_staff, "is_client": is_client}
