from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("trips", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ItineraryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time", models.TimeField(blank=True, null=True)),
                ("title", models.CharField(max_length=160)),
                ("location", models.CharField(blank=True, max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itinerary_items", to="trips.trip")),
            ],
            options={"ordering": ["date", "time", "created_at"]},
        ),
        migrations.CreateModel(
            name="PackingItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("packed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="packing_items", to="trips.trip")),
            ],
            options={"ordering": ["packed", "name"]},
        ),
    ]
