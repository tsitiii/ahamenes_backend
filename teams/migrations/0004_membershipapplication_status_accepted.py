from django.db import migrations, models


def convert_approved_to_accepted(apps, schema_editor):
    MembershipApplication = apps.get_model('teams', 'MembershipApplication')
    MembershipApplication.objects.filter(status='approved').update(status='accepted')


def revert_accepted_to_approved(apps, schema_editor):
    MembershipApplication = apps.get_model('teams', 'MembershipApplication')
    MembershipApplication.objects.filter(status='accepted').update(status='approved')


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_event_eventregistration'),
    ]

    operations = [
        migrations.RunPython(convert_approved_to_accepted, revert_accepted_to_approved),
        migrations.AlterField(
            model_name='membershipapplication',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
                default='pending',
                max_length=20,
            ),
        ),
    ]
