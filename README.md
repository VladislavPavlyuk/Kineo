# KINEO

Cinema: Django with Python templates (DTL).

## Structure

- `backend/` — Django (models, API, templates)
- `backend/kineo/templates/kineo/` — HTML templates (Django Template Language)
- `backend/kineo/static/kineo/` — CSS

## Run

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py create_groups
python manage.py createsuperuser   # for admin
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Pages

- `/` — movie list
- `/movies/<id>/` — movie details, sessions, reviews
- `/movies/new/` — add movie (Staff)
- `/sessions/` — session schedule
- `/login/`, `/register/` — auth
- `/profile/` — my profile
- `/users/<id>/` — user profile

## API (REST)

- `/api/movies/`, `/api/sessions/`, `/api/reviews/` — JSON API (JWT)

## Permissions

- **Guests**: view only
- **Clients** (group): reviews (1 per movie), edit own
- **Staff** (group): movies, sessions, delete any review

```bash
python manage.py create_groups
# Django admin: Users → Groups → Clients or Staff
```

## Models

- **Movie**: title, description, year, duration, genre, poster
- **Session**: movie (FK), date, hall_number
- **Review**: movie (FK), user (FK), text, rating
- **UserProfile**: user (1:1), bio, phone
