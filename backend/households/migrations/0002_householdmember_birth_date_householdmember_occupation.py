# Generated manually for expanded family-member registration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('households', '0002_household_resident_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdmember',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='householdmember',
            name='occupation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
