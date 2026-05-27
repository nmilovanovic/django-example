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
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default="Grad Beograd")

    def __str__(self):
        return f"{self.name}, {self.address}, {self.region}"


class Member(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=512)
    telephone = models.CharField(max_length=15)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}"


class Student(Member):
    school = models.ForeignKey(School, on_delete=models.CASCADE)


class SchoolManager(Member):
    school = models.OneToOneField(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.school.name}, {self.school.address}, {self.school.region}"


class GlobalManager(Member):
    schools = models.ManyToManyField(School)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}, {self.schools.all()}"


class AchievementType(models.Model):
    name = models.CharField(max_length=256)
    points = models.IntegerField()

    def __str__(self):
        return f"{self.name}, {self.points}"


class Achievement(models.Model):
    title = models.CharField(max_length=256)
    date = models.DateField(auto_now_add=True)
    type = models.ForeignKey(AchievementType, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="achievements")

    def __str__(self):
        return f"{self.title}, {self.date}, {self.type}, {self.student}"
