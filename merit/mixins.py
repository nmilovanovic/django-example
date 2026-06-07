from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import Achievement


class StudentRequiredMixin(AccessMixin):
    """Verify that the current user has a student profile."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, "student_profile"):
            messages.error(request, "Permission denied. Student role required.")
            return redirect("merit:login")
        return super().dispatch(request, *args, **kwargs)


class SchoolManagerRequiredMixin(AccessMixin):
    """Verify that the current user has a school manager profile."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, "schoolmanager_profile"):
            messages.error(request, "Permission denied. School Manager role required.")
            return redirect("merit:login")
        return super().dispatch(request, *args, **kwargs)


class ProfessorRequiredMixin(AccessMixin):
    """Verify that the current user has a professor profile."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, "professor_profile"):
            messages.error(request, "Permission denied. Professor role required.")
            return redirect("merit:login")
        return super().dispatch(request, *args, **kwargs)


class AchievementAccessMixin(AccessMixin):
    """Verify the user has permission to view the specific achievement."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        achievement = self.get_object()
        user = request.user
        has_access = False

        if hasattr(user, "student_profile") and user.student_profile == achievement.student:
            has_access = True
        elif hasattr(user, "schoolmanager_profile") and user.schoolmanager_profile.school == achievement.student.school:
            has_access = True
        elif hasattr(user, "professor_profile") and user.professor_profile.school == achievement.student.school:
            has_access = True
        elif hasattr(user, "globalmanager_profile"):
            if achievement.student.school in user.globalmanager_profile.schools.all():
                has_access = True
                
        if not has_access:
            messages.error(request, "You do not have permission to view this achievement.")
            # Redirect to the correct dashboard based on role
            if hasattr(user, "student_profile"):
                return redirect("merit:student_dashboard")
            elif hasattr(user, "schoolmanager_profile"):
                return redirect("merit:manager_dashboard")
            elif hasattr(user, "professor_profile"):
                return redirect("merit:professor_dashboard")
            return redirect("merit:login")

        return super().dispatch(request, *args, **kwargs)
