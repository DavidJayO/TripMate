from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("trips", "0004_map_saved_places_and_sharing")]
    operations = [
        migrations.DeleteModel(name="SavedPlace"),
        migrations.RemoveField(model_name="trip", name="origin_latitude"),
        migrations.RemoveField(model_name="trip", name="origin_longitude"),
        migrations.RemoveField(model_name="trip", name="destination_latitude"),
        migrations.RemoveField(model_name="trip", name="destination_longitude"),
        migrations.RemoveField(model_name="itineraryitem", name="latitude"),
        migrations.RemoveField(model_name="itineraryitem", name="longitude"),
    ]
