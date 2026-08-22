from django.contrib import admin
from django_jsonform.widgets import JSONFormWidget
from .models import Formula,Chapter, PYQ, SimpleUser, ExamDate, FormulaVariable, FormulaConstant, DailyChallenge, Article, Comment, FAQ_SCHEMA


class FormulaVariableInline(admin.TabularInline):
    model = FormulaVariable
    extra = 1

class FormulaConstantInline(admin.TabularInline):
    model = FormulaConstant
    extra = 0



# Register your models here.
class FormulaAdmin(admin.ModelAdmin):
    list_display=("title", "form", "given_by")
    inlines = [FormulaVariableInline, FormulaConstantInline,]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'faqs':
            kwargs['widget'] = JSONFormWidget(schema=FAQ_SCHEMA)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('django_jsonform/react-json-form.css',)
            }
        js = ('django_jsonform/react-json-form.js',)

class DailyChallengeAdmin(admin.ModelAdmin):
    list_display=("date", "scenario_title")

class ArticleAdmin(admin.ModelAdmin):
    list_display=("title")


class CommentAdmin(admin.ModelAdmin):
    list_display=("formula", "comment_text")


admin.site.register(Formula, FormulaAdmin)
admin.site.register(Chapter)
admin.site.register(PYQ)
admin.site.register(DailyChallenge, DailyChallengeAdmin)
admin.site.register(Article)
admin.site.register(Comment, CommentAdmin)


@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth',  'session_id', 'created_at')
    readonly_fields = ('session_id', 'created_at')

@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'exam_date', 'exam_key')