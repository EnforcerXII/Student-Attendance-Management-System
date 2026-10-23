from django.contrib import admin
from .models import Student, Faculty, Subject, Enrolment

admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(Enrolment)
