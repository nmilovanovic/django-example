from django.urls import path
from . import views

app_name = 'merit'

urlpatterns = [
    path("", views.DashboardDispatcherView.as_view(), name="dashboard"),
    path("student/", views.StudentDashboardView.as_view(), name="student_dashboard"),
    path("manager/", views.ManagerDashboardView.as_view(), name="manager_dashboard"),
    path("professor/", views.ProfessorDashboardView.as_view(), name="professor_dashboard"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("verify/<int:achievement_id>/", views.VerifyAchievementView.as_view(), name="verify_achievement"),
    path("achievement/<int:achievement_id>/", views.AchievementDetailView.as_view(), name="achievement_detail"),
]
