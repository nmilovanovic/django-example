from django.apps import AppConfig
from django.db.models.signals import post_migrate

def populate_dummy_data(sender, **kwargs):
    from .models import Student
    if not Student.objects.exists():
        dummy_students = [
            Student(first_name='Alice', last_name='Smith', grade='10th', email='alice.smith@school.edu'),
            Student(first_name='Bob', last_name='Johnson', grade='11th', email='bob.johnson@school.edu'),
            Student(first_name='Charlie', last_name='Williams', grade='9th', email='charlie.williams@school.edu'),
            Student(first_name='Diana', last_name='Brown', grade='12th', email='diana.brown@school.edu'),
            Student(first_name='Ethan', last_name='Davis', grade='10th', email='ethan.davis@school.edu'),
        ]
        Student.objects.bulk_create(dummy_students)
        print("Created dummy students.")

class SchoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school'

    def ready(self):
        post_migrate.connect(populate_dummy_data, sender=self)
