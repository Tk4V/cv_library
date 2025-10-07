from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_requestlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='method',
            field=models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE'), ('OPTIONS', 'OPTIONS'), ('HEAD', 'HEAD')], max_length=10),
        ),
    ]



