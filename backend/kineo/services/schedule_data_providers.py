# add new providers here without changing other code
from kineo.services.schedule_factory import ScheduleDataProvider


PROVIDERS: dict[str, type[ScheduleDataProvider]] = {}


def register_provider(name: str):
    # реєструє провайдер в списку
    def decorator(cls):
        PROVIDERS[name] = cls
        return cls
    return decorator


@register_provider("ukrainian")
class UkrainianScheduleDataProvider:
    # Ukrainian film studios data

    STUDIOS = [
        ("Київська кіностудія ім. О. П. Довженка", "Ukraine"),
        ("Одеська кіностудія художніх фільмів", "Ukraine"),
        ("Київнаукфільм", "Ukraine"),
        ("Укркінохроніка", "Ukraine"),
    ]

    MOVIES = [
        ("Тіні забутих предків", 1964, 97, "драма", "Іван Петрович"),
        ("Білий птах з чорною ознакою", 1971, 97, "драма", "Юрій Іллєнко"),
        ("Відрізані", 1961, 88, "драма", "Михайло Іллєнко"),
        ("Мамай", 2003, 97, "історична драма", "Олесь Санін"),
        ("Захар Беркут", 2019, 106, "історичний екшн", "Ахтем Сеітаблаєв"),
        ("Поводир", 2014, 122, "драма", "Олесь Санін"),
        ("Чужа молитва", 2013, 99, "драма", "Ахтем Сеітаблаєв"),
        ("Земля", 1930, 75, "драма", "Олександр Довженко"),
    ]

    def get_studios(self) -> list[tuple[str, str]]:
        return list(self.STUDIOS)

    def get_movies(self) -> list[tuple[str, int, int, str, str]]:
        return list(self.MOVIES)
