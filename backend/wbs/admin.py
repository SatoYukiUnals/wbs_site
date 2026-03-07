from django.contrib import admin
from .models import WBSItem


@admin.register(WBSItem)
class WBSItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assignee', 'start_date', 'end_date', 'progress']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'assignee']
