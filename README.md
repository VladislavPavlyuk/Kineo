# KINEO

Кінотеатр: Django з шаблонами Python (Jinja2/DTL).

## Структура

- `backend/` — Django (моделі, API, шаблони)
- `backend/kineo/templates/kineo/` — HTML-шаблони (Django Template Language)
- `backend/kineo/static/kineo/` — CSS
- `frontend/` — застарілий React (більше не використовується)

## Запуск

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py create_groups
python manage.py createsuperuser   # для admin
python manage.py runserver
```

Відкрити http://127.0.0.1:8000/

## Сторінки

- `/` — список фільмів
- `/movies/<id>/` — деталі фільму, сеанси, відгуки
- `/movies/new/` — додати фільм (Staff)
- `/sessions/` — розклад сеансів
- `/login/`, `/register/` — авторизація
- `/profile/` — мій профіль
- `/users/<id>/` — профіль користувача

## API (REST)

- `/api/movies/`, `/api/sessions/`, `/api/reviews/` — JSON API (JWT)

## Права доступу

- **Гості**: тільки перегляд
- **Клієнти** (група Clients): відгуки (1 на фільм), редагування власних
- **Персонал** (група Staff): фільми, сеанси, видалення відгуків

```bash
python manage.py create_groups
# Django admin: Users → Groups → Clients або Staff
```

## Моделі

- **Movie**: title, description, year, duration, genre, poster
- **Session**: movie (FK), date, hall_number
- **Review**: movie (FK), user (FK), text, rating
- **UserProfile**: user (1:1), bio, avatar, phone
