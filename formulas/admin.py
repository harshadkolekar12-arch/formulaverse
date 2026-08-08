from django.contrib import admin

from .models import Formula,Chapter, PYQ, SimpleUser, ExamDate, FormulaVariable, FormulaConstant, DailyChallenge


class FormulaVariableInline(admin.TabularInline):
    model = FormulaVariable
    extra = 1

class FormulaConstantInline(admin.TabularInline):
    model = FormulaConstant
    extra = 0



# Register your models here.
class FormulaAdmin(admin.ModelAdmin):
    list_display=("title", "form", "given_by")
    inlines = [FormulaVariableInline, FormulaConstantInline]

class DailyChallengeAdmin(admin.ModelAdmin):
    list_display=("date", "scenario_title")

admin.site.register(Formula, FormulaAdmin)
admin.site.register(Chapter)
admin.site.register(PYQ)
admin.site.register(DailyChallenge, DailyChallengeAdmin)

@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth',  'session_id', 'created_at')
    readonly_fields = ('session_id', 'created_at')

@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'exam_date', 'exam_key')