# Generated by Django 3.1.7 on 2021-02-27 18:12

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('git_prat_id', models.CharField(default=uuid.uuid4, max_length=128)),
                ('title', models.CharField(default='', max_length=256)),
                ('price', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snapshot', models.JSONField(default=dict)),
                ('when_saved', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='GitPrat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('git_prat_id', models.CharField(default='', max_length=128)),
                ('snapshots', models.ManyToManyField(blank=True, to='revertible.Snapshot')),
            ],
        ),
    ]
