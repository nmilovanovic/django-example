import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from merit.models import (
    School,
    Student,
    SchoolManager,
    GlobalManager,
    CompetitionType,
    Competition,
    Achievement,
    Professor,
    CompetitionLevel,
    Placement,
)

User = get_user_model()

# Data arrays
MALE_NAMES = [
    "Nikola",
    "Marko",
    "Stefan",
    "Luka",
    "Aleksandar",
    "Jovan",
    "Nemanja",
    "Miloš",
    "Filip",
    "Dušan",
]
FEMALE_NAMES = [
    "Milica",
    "Jelena",
    "Katarina",
    "Marija",
    "Ana",
    "Jovana",
    "Teodora",
    "Anđela",
    "Sofija",
    "Sara",
]
SURNAMES = [
    "Jovanović",
    "Petrović",
    "Nikolić",
    "Marković",
    "Đorđević",
    "Stojanović",
    "Ilić",
    "Stanković",
    "Pavlović",
    "Milošević",
]
STREETS = [
    "Knez Mihailova",
    "Bulevar kralja Aleksandra",
    "Nemanjina",
    "Kralja Milana",
    "Takovska",
    "Gospodar Jovanova",
    "Bulevar oslobođenja",
    "Njegoševa",
]
CITIES = [
    "Beograd",
    "Novi Sad",
    "Niš",
    "Kragujevac",
    "Subotica",
    "Zrenjanin",
    "Pančevo",
    "Čačak",
    "Kraljevo",
    "Novi Pazar",
]

SCHOOLS = [
    ("Matematička gimnazija", "Kraljice Natalije 37, Beograd", "Belgrade"),
    ("Gimnazija 'Jovan Jovanović Zmaj'", "Zlatne grede 4, Novi Sad", "Vojvodina"),
    ("Prva beogradska gimnazija", "Cara Dušana 61, Beograd", "Belgrade"),
    (
        "Elektrotehnička škola 'Nikola Tesla'",
        "Kraljice Natalije 31, Beograd",
        "Belgrade",
    ),
    ("Vazduhoplovna akademija", "Bulevar vojvode Bojovića 2, Beograd", "Belgrade"),
    (
        "Gimnazija 'Svetozar Marković'",
        "Branka Radičevića 1, Niš",
        "Southern and Eastern Serbia",
    ),
    (
        "Gimnazija 'Bora Stanković'",
        "Vožda Karađorđa 27, Niš",
        "Southern and Eastern Serbia",
    ),
    ("Zemunska gimnazija", "Gradski park 1, Beograd", "Belgrade"),
    (
        "Deseta beogradska gimnazija 'Mihajlo Pupin'",
        "Antifašističke borbe 71, Beograd",
        "Belgrade",
    ),
    (
        "Medicinska škola",
        "Radoja Domanovića 1, Kragujevac",
        "Šumadija and Western Serbia",
    ),
]

COMPETITIONS = [
    ("Republičko takmičenje iz matematike", 100),
    ("Republičko takmičenje iz fizike", 100),
    ("Srpska informatička olimpijada", 120),
    ("Republičko takmičenje iz srpskog jezika i jezičke kulture", 90),
    ("Republičko takmičenje iz hemije", 90),
    ("Republičko takmičenje iz biologije", 90),
    ("Republičko takmičenje iz istorije", 80),
    ("Republičko takmičenje iz geografije", 80),
    ("Smotra istraživačkih radova talenata", 85),
    ("Književna olimpijada", 85),
    ("Republičko takmičenje u atletici (SOŠOV)", 70),
    ("Republičko takmičenje u košarci", 70),
    ("Republičko takmičenje u odbojci", 70),
    ("Republičko takmičenje u plivanju", 70),
    ("Republičko takmičenje muzičkih i baletskih škola Srbije", 80),
    ("Republičko takmičenje iz likovne kulture", 80),
    ("Republičko takmičenje horova i orkestara", 75),
]

ACHIEVEMENT_TITLES = [
    "1. mesto (I nagrada)",
    "2. mesto (II nagrada)",
    "3. mesto (III nagrada)",
    "Pohvala (IV nagrada)",
    "Učešće",
]


def generate_name():
    first_name = random.choice(MALE_NAMES + FEMALE_NAMES)
    last_name = random.choice(SURNAMES)
    return first_name, last_name


def generate_address():
    street = random.choice(STREETS)
    number = random.randint(1, 150)
    city = random.choice(CITIES)
    return f"{street} {number}, {city}"


def generate_phone():
    return f"+3816{random.randint(0, 9)}{random.randint(1000000, 9999999)}"


def generate_email(first_name, last_name, counter):
    # Basic transliteration just in case, though names are in latin, we remove č, ć, ž, š, đ
    first_clean = (
        first_name.replace("đ", "dj")
        .replace("Đ", "Dj")
        .replace("č", "c")
        .replace("ć", "c")
        .replace("ž", "z")
        .replace("š", "s")
    )
    last_clean = (
        last_name.replace("đ", "dj")
        .replace("Đ", "Dj")
        .replace("č", "c")
        .replace("ć", "c")
        .replace("ž", "z")
        .replace("š", "s")
    )
    return f"{first_clean.lower()}.{last_clean.lower()}{counter}@example.com"


def seed(num_students_per_school=10, num_achievements_per_student=3):
    print("Clearing old data...")
    # Delete non-superuser accounts (cascades to profile tables)
    User.objects.filter(is_superuser=False).delete()
    School.objects.all().delete()
    CompetitionType.objects.all().delete()
    Competition.objects.all().delete()
    GlobalManager.objects.all().delete()
    Professor.objects.all().delete()

    print("Creating predefined CompetitionTypes...")
    global_competitions = []
    for name, points in COMPETITIONS:
        comp = CompetitionType.objects.create(
            name=name,
            level=random.choice(CompetitionLevel.choices)[0],
            points_1st_place=points,
            points_2nd_place=int(points*0.8),
            points_3rd_place=int(points*0.6),
            points_participation=int(points*0.2),
        )
        global_competitions.append(comp)

    print("Creating Schools, Managers, Students, and Achievements...")
    user_counter = 1
    schools = []
    for school_name, address, region in SCHOOLS:
        school = School.objects.create(
            name=school_name,
            address=address,
            region=region,
        )
        schools.append(school)

        # School Manager
        mgr_first, mgr_last = generate_name()
        mgr_email = generate_email(mgr_first, mgr_last, user_counter)
        user_counter += 1
        mgr_user = User.objects.create_user(
            username=mgr_email,
            email=mgr_email,
            first_name=mgr_first,
            last_name=mgr_last,
            password="password123",
        )
        SchoolManager.objects.create(
            user=mgr_user,
            address=generate_address(),
            telephone=generate_phone(),
            school=school,
        )

        # Professors
        professors = []
        for _ in range(2):
            prof_first, prof_last = generate_name()
            prof_email = generate_email(prof_first, prof_last, user_counter)
            user_counter += 1
            prof_user = User.objects.create_user(
                username=prof_email,
                email=prof_email,
                first_name=prof_first,
                last_name=prof_last,
                password="password123",
            )
            prof = Professor.objects.create(
                user=prof_user,
                address=generate_address(),
                telephone=generate_phone(),
                school=school,
            )
            professors.append(prof)

        # Competitions
        school_competitions = []
        for global_comp in random.sample(global_competitions, 5):
            sc_comp = Competition.objects.create(
                school=school,
                type=global_comp,
                year=2024,
                professor=random.choice(professors)
            )
            school_competitions.append(sc_comp)

        # Students
        for _ in range(num_students_per_school):
            std_first, std_last = generate_name()
            std_email = generate_email(std_first, std_last, user_counter)
            user_counter += 1
            std_user = User.objects.create_user(
                username=std_email,
                email=std_email,
                first_name=std_first,
                last_name=std_last,
                password="password123",
            )
            student = Student.objects.create(
                user=std_user,
                address=generate_address(),
                telephone=generate_phone(),
                school=school,
            )

            # Achievements
            for _ in range(num_achievements_per_student):
                Achievement.objects.create(
                    title=random.choice(ACHIEVEMENT_TITLES),
                    competition=random.choice(school_competitions),
                    student=student,
                    placement=random.choice(Placement.choices)[0],
                    is_verified=random.choice([True, False]),
                )

    print("Creating Global Managers...")
    for _ in range(2):
        gm_first, gm_last = generate_name()
        gm_email = generate_email(gm_first, gm_last, user_counter)
        user_counter += 1
        gm_user = User.objects.create_user(
            username=gm_email,
            email=gm_email,
            first_name=gm_first,
            last_name=gm_last,
            password="password123",
        )
        gm = GlobalManager.objects.create(
            user=gm_user,
            address=generate_address(),
            telephone=generate_phone(),
        )
        gm.schools.set(random.sample(schools, k=random.randint(1, len(schools))))

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
