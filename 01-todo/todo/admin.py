from django.contrib import admin
from .models import Todo

# Register your models here.
@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'completed', 'owner', 'created_at')
    list_filter = ('completed', 'created_at', 'owner')
    search_fields = ('title', 'description')
    list_editable = ('completed',)
    date_hierarchy = 'created_at'