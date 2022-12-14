# Generated by Django 3.2.16 on 2022-10-09 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shorten', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shorturl',
            name='num_clicks',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, db_index=True, null=True)),
                ('short_url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', related_query_name='click', to='shorten.shorturl')),
            ],
        ),
    ]
