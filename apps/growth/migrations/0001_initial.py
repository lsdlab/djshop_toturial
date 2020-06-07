# Generated by Django 3.0.1 on 2019-12-26 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_points', models.IntegerField()),
                ('to_points', models.IntegerField()),
            ],
            options={
                'verbose_name': '签到日志',
                'verbose_name_plural': '签到日志',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('left', models.IntegerField(default=10)),
                ('shortuuid', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': '邀请',
                'verbose_name_plural': '邀请',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('desc', models.CharField(default='', max_length=255)),
                ('invite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invite_logs', to='growth.Invite')),
            ],
            options={
                'verbose_name': '邀请日志',
                'verbose_name_plural': '邀请日志',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
    ]
