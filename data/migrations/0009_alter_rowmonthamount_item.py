# Generated by Django 4.0.5 on 2022-06-10 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_rowmonthamount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rowmonthamount',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.itemaccount'),
        ),
    ]
