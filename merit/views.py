from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, View

from .models import Achievement, Competition
from .forms import AchievementForm, EnableCompetitionForm
from .mixins import (
    StudentRequiredMixin, 
    SchoolManagerRequiredMixin, 
    ProfessorRequiredMixin, 
    AchievementAccessMixin
)

class CustomLoginView(LoginView):
    template_name = "login.html"
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)
        
    def get_success_url(self):
        user = self.request.user
        if hasattr(user, "student_profile"):
            return reverse_lazy("merit:student_dashboard")
        elif hasattr(user, "schoolmanager_profile"):
            return reverse_lazy("merit:manager_dashboard")
        elif hasattr(user, "professor_profile"):
            return reverse_lazy("merit:professor_dashboard")
        return reverse_lazy("merit:dashboard") # Default fallback

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("merit:login")
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

class DashboardDispatcherView(LoginRequiredMixin, View):
    """Redirects authenticated users to their specific dashboard."""
    def get(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, "student_profile"):
            return redirect("merit:student_dashboard")
        elif hasattr(user, "schoolmanager_profile"):
            return redirect("merit:manager_dashboard")
        elif hasattr(user, "professor_profile"):
            return redirect("merit:professor_dashboard")
        else:
            messages.error(request, "Your account does not have an assigned role.")
            return redirect("merit:logout")

class StudentDashboardView(LoginRequiredMixin, StudentRequiredMixin, CreateView):
    template_name = "student_dashboard.html"
    form_class = AchievementForm
    success_url = reverse_lazy("merit:student_dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.student_profile.school
        return kwargs

    def form_valid(self, form):
        achievement = form.save(commit=False)
        achievement.student = self.request.user.student_profile
        achievement.is_verified = False
        achievement.save()
        messages.success(self.request, "Achievement submitted successfully! Waiting for verification.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['student'] = student
        context['achievements'] = student.achievements.all().order_by("-date", "-id")
        context['total_score'] = student.get_total_score()
        return context

class ManagerDashboardView(LoginRequiredMixin, SchoolManagerRequiredMixin, CreateView):
    template_name = "manager_dashboard.html"
    form_class = EnableCompetitionForm
    success_url = reverse_lazy("merit:manager_dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.schoolmanager_profile.school
        return kwargs

    def form_valid(self, form):
        competition = form.save(commit=False)
        competition.school = self.request.user.schoolmanager_profile.school
        competition.save()
        messages.success(self.request, "Competition enabled successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = self.request.user.schoolmanager_profile
        school = manager.school
        
        context['manager'] = manager
        context['school'] = school
        context['comp_form'] = context['form'] # Alias for the template
        
        context['pending_achievements'] = Achievement.objects.filter(
            student__school=school, is_verified=False
        ).select_related("student", "competition__type").order_by("date")
        
        context['verified_achievements'] = Achievement.objects.filter(
            student__school=school, is_verified=True
        ).select_related("student", "competition__type").order_by("-date")[:10]
        
        context['enabled_competitions'] = Competition.objects.filter(
            school=school
        ).select_related("type", "professor")
        
        context['top_students'] = school.get_top_students()
        context['is_schoolmanager'] = True
        return context

class ProfessorDashboardView(LoginRequiredMixin, ProfessorRequiredMixin, TemplateView):
    template_name = "professor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = self.request.user.professor_profile
        school = manager.school
        
        context['professor'] = manager
        context['school'] = school
        
        context['pending_achievements'] = Achievement.objects.filter(
            student__school=school, 
            is_verified=False, 
            competition__professor=manager
        ).select_related("student", "competition__type").order_by("date")

        context['verified_achievements'] = Achievement.objects.filter(
            student__school=school, 
            is_verified=True,
            competition__professor=manager
        ).select_related("student", "competition__type").order_by("-date")[:10]

        context['enabled_competitions'] = Competition.objects.filter(
            school=school, professor=manager
        ).select_related("type")
        
        context['is_professor'] = True
        return context

class VerifyAchievementView(LoginRequiredMixin, ProfessorRequiredMixin, View):
    def post(self, request, achievement_id):
        achievement = get_object_or_404(Achievement, id=achievement_id)
        manager = request.user.professor_profile

        if achievement.student.school != manager.school:
            messages.error(request, "You can only verify achievements for your school.")
            return redirect("merit:professor_dashboard")

        if achievement.competition.professor != manager:
            messages.error(request, "You can only verify achievements for competitions you lead.")
            return redirect("merit:professor_dashboard")

        achievement.is_verified = True
        achievement.save()
        messages.success(request, f"Verified achievement: {achievement.title}")
        return redirect("merit:professor_dashboard")

class AchievementDetailView(LoginRequiredMixin, AchievementAccessMixin, DetailView):
    model = Achievement
    template_name = "achievement_detail.html"
    context_object_name = "achievement"
    pk_url_kwarg = "achievement_id"

    def get_queryset(self):
        return Achievement.objects.select_related("student", "competition__type", "competition__professor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        achievement = self.object
        context["is_professor"] = (
            hasattr(user, "professor_profile") and 
            achievement.competition.professor == user.professor_profile
        )
        return context
