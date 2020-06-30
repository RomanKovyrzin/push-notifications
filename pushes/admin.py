from django.contrib import admin
from .models import Push, Option

# Register your models here.

@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'send_date', 'sender')
    list_filter = ('title', 'creation_date', 'send_date', 'sender')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass