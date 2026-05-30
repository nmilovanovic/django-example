from django.test import TestCase
from django.contrib.auth import get_user_model
from merit.models import School, Student, CompetitionType, Competition, Achievement
from django.db.models.functions import Coalesce

class StudentRatingTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test School", address="123 Test St")

        User = get_user_model()
        user1 = User.objects.create_user(
            username="alice", email="alice@test.com", first_name="Alice", last_name="A"
        )
        user2 = User.objects.create_user(
            username="bob", email="bob@test.com", first_name="Bob", last_name="B"
        )

        self.student1 = Student.objects.create(
            user=user1, address="A", telephone="123", school=self.school
        )
        self.student2 = Student.objects.create(
            user=user2, address="B", telephone="123", school=self.school
        )

        self.cert_type = CompetitionType.objects.create(name="Cert", points_1st_place=10)
        self.medal_type = CompetitionType.objects.create(name="Medal", points_1st_place=50)

        self.cert_comp = Competition.objects.create(type=self.cert_type, school=self.school, year=2024)
        self.medal_comp = Competition.objects.create(type=self.medal_type, school=self.school, year=2024)

    def test_student_total_score_only_counts_verified(self):
        Achievement.objects.create(
            title="Unverified Cert",
            competition=self.cert_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=False,
        )
        Achievement.objects.create(
            title="Verified Medal",
            competition=self.medal_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=True,
        )
        Achievement.objects.create(
            title="Verified Cert",
            competition=self.cert_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=True,
        )

        # Unverified = 10, Verified = 50 + 10 = 60
        self.assertEqual(self.student1.get_total_score(), 60)

    def test_school_get_top_students(self):
        # Student 1 has 60 verified points
        Achievement.objects.create(
            title="Verified Medal",
            competition=self.medal_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=True,
        )
        Achievement.objects.create(
            title="Verified Cert",
            competition=self.cert_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=True,
        )

        # Student 2 has 100 verified points
        Achievement.objects.create(
            title="Verified Medal 1",
            competition=self.medal_comp,
            placement='1ST_PLACE',
            student=self.student2,
            is_verified=True,
        )
        Achievement.objects.create(
            title="Verified Medal 2",
            competition=self.medal_comp,
            placement='1ST_PLACE',
            student=self.student2,
            is_verified=True,
        )
        Achievement.objects.create(
            title="Unverified Medal",
            competition=self.medal_comp,
            placement='1ST_PLACE',
            student=self.student2,
            is_verified=False,
        )

        top_students = self.school.get_top_students()
        self.assertEqual(len(top_students), 2)

        # Total score gets annotated
        self.assertEqual(top_students[0].id, self.student2.id)
        self.assertEqual(top_students[0].total_score, 100)

        self.assertEqual(top_students[1].id, self.student1.id)
        self.assertEqual(top_students[1].total_score, 60)

    def test_student_no_verified_achievements(self):
        Achievement.objects.create(
            title="Unverified Cert",
            competition=self.cert_comp,
            placement='1ST_PLACE',
            student=self.student1,
            is_verified=False,
        )
        self.assertEqual(self.student1.get_total_score(), 0)

        top_students = self.school.get_top_students()

        # if the total score is None, it should fall back to 0 or we can just check if they are ranked correctly
        student_scores = [student.total_score for student in top_students]
        # They should both be None or 0
        self.assertTrue(all(score in (0, None) for score in student_scores))
