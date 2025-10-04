from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0023_stage_average_wait_time_stage_environment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='water_quality',
            field=models.CharField(blank=True, choices=[('CLEAN', 'Sauber'), ('SLIGHTLY_POLLUTED', 'Leicht verschmutzt'), ('HEAVILY_POLLUTED', 'Stark verschmutzt'), ('ABSOLUTE_SEWER', 'Absolute Kloake')], help_text='Water quality classification for riverwaves', max_length=20),
        ),
    ]
