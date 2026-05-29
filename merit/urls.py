from django.urls import path
from . import views

app_name = 'merit'

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify/<int:achievement_id>/", views.verify_achievement, name="verify_achievement"),
]
