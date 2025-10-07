from django.contrib import admin
from .models import Project, Bug

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manager")
    search_fields = ("name", "manager__username", "manager__email")
    filter_horizontal = ("qas", "developers")


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "type", "status", "assigned_to", "created_at")
    list_filter = ("type", "status", "project")
    search_fields = ("title", "project__name", "assigned_to__username")
