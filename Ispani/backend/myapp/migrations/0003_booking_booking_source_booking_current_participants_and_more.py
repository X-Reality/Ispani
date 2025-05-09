# Generated by Django 5.1.7 on 2025-04-07 07:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_eventtag_event_eventcomment_eventmedia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_source',
            field=models.CharField(choices=[('internal', 'App Booking'), ('calendly', 'Calendly Booking')], default='internal', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='current_participants',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='booking',
            name='is_group_session',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='max_participants',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='payment',
            name='provider',
            field=models.CharField(default='stripe', max_length=20),
        ),
        migrations.AddField(
            model_name='payment',
            name='student',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.tutoravailability'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='myapp.booking'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='CalendlyEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendly_event_id', models.CharField(max_length=255, unique=True)),
                ('calendly_event_uri', models.URLField()),
                ('event_type_name', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('invitee_email', models.EmailField(max_length=254)),
                ('invitee_name', models.CharField(max_length=255)),
                ('location', models.TextField(blank=True, null=True)),
                ('cancellation_url', models.URLField(blank=True, null=True)),
                ('reschedule_url', models.URLField(blank=True, null=True)),
                ('status', models.CharField(default='active', max_length=20)),
                ('is_group_event', models.BooleanField(default=False)),
                ('max_participants', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendly_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='calendly_event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookings', to='myapp.calendlyevent'),
        ),
        migrations.CreateModel(
            name='ExternalCalendarConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('calendly', 'Calendly'), ('google', 'Google Calendar'), ('microsoft', 'Microsoft Calendar')], max_length=20)),
                ('provider_user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('calendly_username', models.CharField(blank=True, max_length=255, null=True)),
                ('calendly_uri', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_connections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'provider')},
            },
        ),
        migrations.CreateModel(
            name='GroupSessionParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.CharField(default='pending', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='myapp.booking')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('booking', 'student')},
            },
        ),
        migrations.CreateModel(
            name='MeetingProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('zoom', 'Zoom'), ('google_meet', 'Google Meet'), ('microsoft_teams', 'Microsoft Teams'), ('jitsi', 'Jitsi Meet')], max_length=20)),
                ('provider_user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_providers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'provider')},
            },
        ),
    ]
