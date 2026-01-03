# Generated manually for room_type max_length change

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuilder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(
                choices=[
                    ('ATTACHED_BED_BATH', 'Attached Bedroom + Bath'),
                    ('KITCHEN', 'Kitchen'),
                    ('LIVING', 'Living Room'),
                    ('KITCHEN_LIVING_DINING_HUB', 'Kitchen Living Dining Hub'),
                    ('HALL', 'Hallway'),
                    ('STAIR', 'Stairway'),
                    ('STUDYROOM', 'Study Room'),
                    ('STORAGE', 'Storage'),
                ],
                max_length=30
            ),
        ),
    ]
