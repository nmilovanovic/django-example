from django.contrib import admin
from .models import School, Member, Student, SchoolManager, GlobalManager, AchievementType, Achievement

admin.site.register(School)
admin.site.register(Member)
admin.site.register(Student)
admin.site.register(SchoolManager)
admin.site.register(GlobalManager)
admin.site.register(AchievementType)
admin.site.register(Achievement)
