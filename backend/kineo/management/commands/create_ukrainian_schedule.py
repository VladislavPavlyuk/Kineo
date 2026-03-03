# command creates schedule via factory
from django.core.management.base import BaseCommand

from kineo.services import ScheduleFactory
from kineo.services.schedule_data_providers import (
    UkrainianScheduleDataProvider,
    PROVIDERS,
)


class Command(BaseCommand):
    help = "Creates Ukrainian studios, movies and session schedule"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="скільки днів розкладу зробити",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="clear all data first",
        )
        parser.add_argument(
            "--provider",
            default="ukrainian",
            choices=list(PROVIDERS.keys()),
            help="data provider for studios and movies",
        )

    def handle(self, *args, **options):
        provider_cls = PROVIDERS[options["provider"]]
        factory = ScheduleFactory(provider_cls())

        if options["clear"]:
            factory.clear()
            self.stdout.write("Data cleared.")

        studios = factory.create_studios()
        self.stdout.write(f"Studios: {len(studios)}")

        movies = factory.create_movies(studios)
        self.stdout.write(f"Ukrainian studio movies: {len(movies)}")

        sessions_created = factory.create_schedule(
            movies=movies,
            days=options["days"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Sessions created: {sessions_created}. "
                f"Schedule for {options['days']} days."
            )
        )
