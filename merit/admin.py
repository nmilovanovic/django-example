from django.contrib import admin
from .models import School, Student, SchoolManager, GlobalManager, AchievementType, Achievement

admin.site.register(School)
admin.site.register(Student)
admin.site.register(SchoolManager)
admin.site.register(GlobalManager)
admin.site.register(AchievementType)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'type', 'date', 'is_verified')
    list_editable = ('is_verified',)
    list_filter = ('is_verified', 'type', 'student__school')

admin.site.register(Achievement, AchievementAdmin)
