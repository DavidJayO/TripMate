from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Trip", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("destination", models.CharField(max_length=160)),
        ("origin", models.CharField(default="Manila", max_length=160)),
        ("start_date", models.DateField()),
        ("end_date", models.DateField()),
        ("budget", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
        ("currency", models.CharField(default="USD", max_length=3)),
        ("target_currency", models.CharField(default="PHP", max_length=3)),
        ("country_code", models.CharField(blank=True, help_text="Optional ISO country code for holiday lookup, e.g. JP", max_length=2)),
        ("notes", models.TextField(blank=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trips", to=settings.AUTH_USER_MODEL)),
    ], options={"ordering": ["start_date", "destination"]})]
