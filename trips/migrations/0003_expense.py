from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("trips", "0002_itineraryitem_packingitem")]
    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("category", models.CharField(choices=[("transport", "Transport"), ("accommodation", "Accommodation"), ("food", "Food & drinks"), ("activities", "Activities"), ("shopping", "Shopping"), ("other", "Other")], default="other", max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.01)])),
                ("date", models.DateField()),
                ("notes", models.CharField(blank=True, max_length=240)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to="trips.trip")),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
    ]
