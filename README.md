# TripMate

A Django trip planner with user accounts, trip CRUD, an admin dashboard, and travel details from Open-Meteo, Nominatim, OSRM, Frankfurter, and Nager.Date.

Trip pages include a day-by-day itinerary (activity, date, time, location, and notes) and a packing checklist with completion tracking.
They also include expense tracking by category, with totals compared against the trip budget.
Owners can share a trip with existing accounts as a viewer or itinerary editor; editors can manage itinerary activities, while trip settings, expenses, and packing remain owner-managed.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize the database: `python manage.py migrate`
4. Create an administrator: `python manage.py createsuperuser`
5. Start the server: `python manage.py runserver`

SQLite is the default. Set `DATABASE_URL` to a PostgreSQL connection URL to use PostgreSQL. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS` for deployment. Admin dashboard access uses Django's `is_staff` role; create staff users through `/admin/`.

External calls have short timeouts and fail gracefully. Nominatim searches run only when opening a trip detail page. Follow [Nominatim's usage policy](https://operations.osmfoundation.org/policies/nominatim/) and avoid automated/high-volume lookups.
