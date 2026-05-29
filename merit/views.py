from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Achievement
from .forms import AchievementForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('merit:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('merit:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('merit:login')

@login_required(login_url='merit:login')
def dashboard(request):
    user = request.user
    
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        
        # Handle Achievement Submission
        if request.method == 'POST':
            form = AchievementForm(request.POST)
            if form.is_valid():
                achievement = form.save(commit=False)
                achievement.student = student
                achievement.is_verified = False
                achievement.save()
                messages.success(request, "Achievement submitted successfully! Waiting for verification.")
                return redirect('merit:dashboard')
        else:
            form = AchievementForm()
            
        achievements = student.achievements.all().order_by('-date', '-id')
        total_score = student.get_total_score()
        
        context = {
            'student': student,
            'achievements': achievements,
            'total_score': total_score,
            'form': form,
        }
        return render(request, 'student_dashboard.html', context)
        
    elif hasattr(user, 'schoolmanager_profile'):
        manager = user.schoolmanager_profile
        school = manager.school
        
        # Get pending achievements for students in this school
        pending_achievements = Achievement.objects.filter(
            student__school=school, 
            is_verified=False
        ).select_related('student', 'type').order_by('date')
        
        # Get verified achievements
        verified_achievements = Achievement.objects.filter(
            student__school=school, 
            is_verified=True
        ).select_related('student', 'type').order_by('-date')[:10]  # Show recent 10
        
        top_students = school.get_top_students()
        
        context = {
            'manager': manager,
            'school': school,
            'pending_achievements': pending_achievements,
            'verified_achievements': verified_achievements,
            'top_students': top_students,
        }
        return render(request, 'manager_dashboard.html', context)
        
    else:
        messages.error(request, "Your account does not have an assigned role.")
        return redirect('merit:logout')

@login_required(login_url='merit:login')
@require_POST
def verify_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    user = request.user
    
    # Check permissions
    if not hasattr(user, 'schoolmanager_profile'):
        messages.error(request, "Permission denied.")
        return redirect('merit:dashboard')
        
    manager = user.schoolmanager_profile
    if achievement.student.school != manager.school:
        messages.error(request, "You can only verify achievements for your school.")
        return redirect('merit:dashboard')
        
    achievement.is_verified = True
    achievement.save()
    messages.success(request, f"Verified achievement: {achievement.title}")
    
    return redirect('merit:dashboard')
