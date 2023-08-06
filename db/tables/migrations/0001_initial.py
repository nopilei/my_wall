# Generated by Django 4.2.2 on 2023-07-02 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserSubscribtion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('channel_id', models.IntegerField()),
            ],
        ),
        migrations.AddConstraint(
            model_name='usersubscribtion',
            constraint=models.UniqueConstraint(fields=('user_id', 'channel_id'), name='unique_subscribtion_per_user'),
        ),
    ]
