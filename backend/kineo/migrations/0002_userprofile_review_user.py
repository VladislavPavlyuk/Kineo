from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def clear_reviews(apps, schema_editor):
    Review = apps.get_model("kineo", "Review")
    Review.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("kineo", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bio", models.TextField(blank=True)),
                ("avatar", models.ImageField(blank=True, null=True, upload_to="avatars/")),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(clear_reviews),
        migrations.RemoveField(model_name="review", name="username"),
        migrations.AddField(
            model_name="review",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name="review",
            unique_together={("movie", "user")},
        ),
    ]
