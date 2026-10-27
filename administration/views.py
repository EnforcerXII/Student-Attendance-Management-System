from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from attendance.models import AuditLog


@login_required
def audit_log_view(request):
    """View system audit logs (SAM-NF-006, SAM-SR-005, TC-AUDIT-01)."""
    if request.user.role != "ADMIN":
        raise PermissionDenied
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")[:200]
    return render(request, "administration/audit_logs.html", {"logs": logs})
