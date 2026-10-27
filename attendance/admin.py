from django.contrib import admin
from .models import AttendanceSession, Attendance, AuditLog

admin.site.register(AttendanceSession)
admin.site.register(Attendance)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "entity", "entity_id")
    list_filter = ("action", "entity", "timestamp")
    search_fields = ("user__username", "entity", "entity_id", "details")
    readonly_fields = ("user", "action", "entity", "entity_id", "old_value", "new_value", "reason", "timestamp")
