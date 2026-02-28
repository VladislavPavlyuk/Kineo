from kineo.models import Studio


class StudioService:
    @staticmethod
    def get_all():
        return Studio.objects.all()
