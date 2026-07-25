from django.contrib import admin

from .models import Formula,Chapter, PYQ, SimpleUser

# Register your models here.
class FormulaAdmin(admin.ModelAdmin):
    list_display=("title", "form", "given_by")

admin.site.register(Formula, FormulaAdmin)
admin.site.register(Chapter)
admin.site.register(PYQ)


@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ('date_of_birth', 'session_id', 'created_at')
    readonly_fields = ('session_id', 'created_at')