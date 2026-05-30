from django.conf import settings
from django.db import models


class School(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=512)
    REGION_CHOICES = [
        ("Nisavski", "Nisavski"),
        ("Borski", "Borski"),
        ("Zajecarski", "Zajecarski"),
        ("Toplicki", "Toplicki"),
        ("Podunavski", "Podunavski"),
        ("Kosovo i Metohija", "Kosovo i Metohija"),
        ("Grad Beograd", "Grad Beograd"),
    ]
    region = models.CharField(
        max_length=50, choices=REGION_CHOICES, default="Grad Beograd"
    )

    def get_top_students(self):
        from django.db.models import Sum, Q, Case, When, F

        score_case = Case(
            When(achievements__placement='1ST_PLACE', then=F('achievements__competition__type__points_1st_place')),
            When(achievements__placement='2ND_PLACE', then=F('achievements__competition__type__points_2nd_place')),
            When(achievements__placement='3RD_PLACE', then=F('achievements__competition__type__points_3rd_place')),
            When(achievements__placement='PARTICIPATION', then=F('achievements__competition__type__points_participation')),
            default=0
        )
        return self.student_set.annotate(
            total_score=Sum(score_case, filter=Q(achievements__is_verified=True))
        ).order_by("-total_score", "user__first_name", "user__last_name")

    def __str__(self):
        return f"{self.name}, {self.address}, {self.region}"


class Member(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_profile",
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=512)
    telephone = models.CharField(max_length=15)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        self.user.first_name = value

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
        self.user.last_name = value

    @property
    def email(self):
        return self.user.email

    @email.setter
    def email(self, value):
        self.user.email = value

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}"


class Student(Member):
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def get_total_score(self):
        from django.db.models import Sum, Case, When, F

        score_case = Case(
            When(placement='1ST_PLACE', then=F('competition__type__points_1st_place')),
            When(placement='2ND_PLACE', then=F('competition__type__points_2nd_place')),
            When(placement='3RD_PLACE', then=F('competition__type__points_3rd_place')),
            When(placement='PARTICIPATION', then=F('competition__type__points_participation')),
            default=0
        )
        result = self.achievements.filter(is_verified=True).aggregate(
            total=Sum(score_case)
        )
        return result["total"] or 0

class Professor(Member):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="professors")

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email} (Professor)"

class SchoolManager(Member):
    school = models.OneToOneField(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.school.name}, {self.school.address}, {self.school.region}"


class GlobalManager(Member):
    schools = models.ManyToManyField(School)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}, {self.schools.all()}"


class CompetitionLevel(models.TextChoices):
    MUNICIPAL = 'MUNICIPAL', 'Opštinsko'
    DISTRICT = 'DISTRICT', 'Okružno'
    REPUBLIC = 'REPUBLIC', 'Republičko'
    INTERNATIONAL = 'INTERNATIONAL', 'Međunarodno'

class Placement(models.TextChoices):
    PLACE_1ST = '1ST_PLACE', '1. mesto'
    PLACE_2ND = '2ND_PLACE', '2. mesto'
    PLACE_3RD = '3RD_PLACE', '3. mesto'
    PARTICIPATION = 'PARTICIPATION', 'Učešće'

class CompetitionType(models.Model):
    name = models.CharField(max_length=256)
    level = models.CharField(max_length=20, choices=CompetitionLevel.choices)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name="custom_competition_types")
    
    points_1st_place = models.IntegerField(default=0)
    points_2nd_place = models.IntegerField(default=0)
    points_3rd_place = models.IntegerField(default=0)
    points_participation = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

class Competition(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="competitions")
    type = models.ForeignKey(CompetitionType, on_delete=models.CASCADE, related_name="competitions")
    year = models.IntegerField()
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_competitions")

    def __str__(self):
        return f"{self.type.name} u {self.school.name} ({self.year})"

class Achievement(models.Model):
    title = models.CharField(max_length=256)
    date = models.DateField(auto_now_add=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="achievements")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="achievements"
    )
    placement = models.CharField(max_length=20, choices=Placement.choices)
    is_verified = models.BooleanField(default=False)

    @property
    def points(self):
        if self.placement == '1ST_PLACE':
            return self.competition.type.points_1st_place
        elif self.placement == '2ND_PLACE':
            return self.competition.type.points_2nd_place
        elif self.placement == '3RD_PLACE':
            return self.competition.type.points_3rd_place
        elif self.placement == 'PARTICIPATION':
            return self.competition.type.points_participation
        return 0

    def __str__(self):
        return f"{self.title}, {self.date}, {self.competition.type.name}, {self.student}"
