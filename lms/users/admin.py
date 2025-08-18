from typing import Any
from django.contrib import admin
from users.models import MemberUser

from django.contrib.auth.admin import UserAdmin

# Register your models here.
class MemberUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ['is_student', 'is_instructor', 'wants_to_be_instructor']}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ['is_student', 'is_instructor']}),
    )

    list_display = UserAdmin.list_display + ('is_student', 'is_instructor', 'wants_to_be_instructor')
    list_filter = UserAdmin.list_filter + ('is_student', 'is_instructor', 'wants_to_be_instructor')

admin.site.register(MemberUser, MemberUserAdmin)