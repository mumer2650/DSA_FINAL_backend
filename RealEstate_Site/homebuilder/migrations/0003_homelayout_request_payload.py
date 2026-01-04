# Generated migration for adding request_payload field to HomeLayout

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuilder', '0002_alter_room_room_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='homelayout',
            name='request_payload',
            field=models.JSONField(default=dict),
        ),
    ]
