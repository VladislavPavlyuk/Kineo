from kineo.models import Movie


class MovieService:

    @staticmethod
    def get_all():
        return Movie.objects.all()
