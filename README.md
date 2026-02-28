# KINEO

Кінотеатр: Django REST API + React Vite frontend.

## Структура

- `backend/` — Django + DRF (моделі, API)
- `frontend/` — React + TypeScript + Vite

## Запуск

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # для admin
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Відкрити http://localhost:5173 (Vite проксує /api та /media на Django).

## API

- `GET/POST /api/movies/` — список, створення
- `GET/PATCH/DELETE /api/movies/:id/` — деталі, оновлення, видалення
- `GET /api/movies/:id/sessions/` — сеанси фільму
- `GET/POST /api/movies/:id/reviews/` — відгуки фільму
- `GET /api/sessions/?movie=id` — сеанси (опційно по фільму)

## Моделі

- **Movie**: title, description, year, duration, genre, poster
- **Session**: movie (FK), date, hall_number
- **Review**: movie (FK), username, text, rating, created_at
