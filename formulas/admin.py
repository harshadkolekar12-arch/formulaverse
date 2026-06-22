from django.contrib import admin

from .models import Formula,Category

# Register your models here.
class FormulaAdmin(admin.ModelAdmin):
    list_display=("title", "form", "given_by")

admin.site.register(Formula, FormulaAdmin)
admin.site.register(Category)


