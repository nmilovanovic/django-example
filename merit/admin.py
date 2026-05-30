from django.contrib import admin
from .models import (
    School,
    Student,
    SchoolManager,
    GlobalManager,
    CompetitionType,
    Competition,
    Achievement,
    Professor,
)

admin.site.register(School)
admin.site.register(Student)
admin.site.register(SchoolManager)
admin.site.register(GlobalManager)
admin.site.register(CompetitionType)
admin.site.register(Competition)
admin.site.register(Professor)

class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "competition", "placement", "date", "is_verified")
    list_editable = ("is_verified",)
    list_filter = ("is_verified", "competition", "student__school")


admin.site.register(Achievement, AchievementAdmin)
