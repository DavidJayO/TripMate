from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0003_expense"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField("trip", "origin_latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField("trip", "origin_longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField("trip", "destination_latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField("trip", "destination_longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField("itineraryitem", "latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField("itineraryitem", "longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.CreateModel(
            name="SavedPlace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("address", models.CharField(max_length=240)),
                ("notes", models.CharField(blank=True, max_length=240)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_places", to="trips.trip")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="TripMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("viewer", "Can view"), ("editor", "Can edit itinerary")], default="viewer", max_length=10)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="trips.trip")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shared_trips", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["user__username"]},
        ),
        migrations.AddConstraint("tripmembership", models.UniqueConstraint(fields=("trip", "user"), name="unique_trip_member")),
    ]
