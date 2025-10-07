from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_requestlog_method_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='method',
            field=models.CharField(max_length=10),
        ),
    ]









