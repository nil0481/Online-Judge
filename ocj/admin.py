from django.contrib import admin
from .models import Problem,  Testcase, Submissions, Leaderboard


class TestcaseInline(admin.TabularInline):
    model = Testcase
    extra = 3

class TestcaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'input', 'output')

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [TestcaseInline]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'verdict', 'submission_time')
    list_filter = ('problem', 'language', 'verdict')
    # inlines = [TestcaseInline]


class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score')


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submissions, SubmissionAdmin)
admin.site.register(Testcase,TestcaseAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
