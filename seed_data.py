import os
import django
from faker import Faker
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from merit.models import School, Student, SchoolManager, GlobalManager, AchievementType, Achievement

fake = Faker()

def seed(num_schools=5, num_students_per_school=10, num_achievements_per_student=3):
    print("Clearing old data...")
    # Because of CASCADE, deleting schools deletes managers, students, and achievements
    School.objects.all().delete()
    AchievementType.objects.all().delete()
    GlobalManager.objects.all().delete()

    print("Creating AchievementTypes...")
    achievement_types = []
    for _ in range(5):
        at = AchievementType.objects.create(
            name=fake.word().capitalize() + " Certificate",
            points=random.randint(10, 100)
        )
        achievement_types.append(at)

    print("Creating Schools, Managers, Students, and Achievements...")
    schools = []
    for _ in range(num_schools):
        school = School.objects.create(
            name=fake.company() + " School",
            address=fake.address().replace('\n', ', '),
            region=random.choice(School.REGION_CHOICES)[0]
        )
        schools.append(school)

        # School Manager
        SchoolManager.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            address=fake.address().replace('\n', ', '),
            telephone=fake.msisdn()[:15],
            school=school
        )

        # Students
        for _ in range(num_students_per_school):
            student = Student.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                address=fake.address().replace('\n', ', '),
                telephone=fake.msisdn()[:15],
                school=school
            )

            # Achievements
            for _ in range(num_achievements_per_student):
                Achievement.objects.create(
                    title=fake.catch_phrase(),
                    type=random.choice(achievement_types),
                    student=student
                )

    print("Creating Global Managers...")
    for _ in range(2):
        gm = GlobalManager.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            address=fake.address().replace('\n', ', '),
            telephone=fake.msisdn()[:15]
        )
        gm.schools.set(random.sample(schools, k=random.randint(1, len(schools))))

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
