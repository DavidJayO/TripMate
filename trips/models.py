from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
class Trip(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips")
    destination = models.CharField(max_length=160)
    origin = models.CharField(max_length=160, default="Manila")
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    target_currency = models.CharField(max_length=3, default="PHP")
    country_code = models.CharField(max_length=2, blank=True, help_text="Optional ISO country code for holiday lookup, e.g. JP")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["start_date", "destination"]
    def __str__(self):
        return f"{self.destination} ({self.start_date})"

class ItineraryItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="itinerary_items")
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    title = models.CharField(max_length=160)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time", "created_at"]

    def __str__(self):
        return f"{self.date}: {self.title}"

class PackingItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="packing_items")
    name = models.CharField(max_length=160)
    packed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["packed", "name"]

    def __str__(self):
        return self.name

class Expense(models.Model):
    class Category(models.TextChoices):
        TRANSPORT = "transport", "Transport"
        ACCOMMODATION = "accommodation", "Accommodation"
        FOOD = "food", "Food & drinks"
        ACTIVITIES = "activities", "Activities"
        SHOPPING = "shopping", "Shopping"
        OTHER = "other", "Other"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField()
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.amount} {self.trip.currency}"

class TripMembership(models.Model):
    class Role(models.TextChoices):
        VIEWER = "viewer", "Can view"
        EDITOR = "editor", "Can edit itinerary"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_trips")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]
        constraints = [models.UniqueConstraint(fields=["trip", "user"], name="unique_trip_member")]

    def __str__(self):
        return f"{self.user} · {self.trip} ({self.role})"
