

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('College & Role', {
            'fields': ('role', 'college'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('College & Role', {
            'fields': ('role', 'college'),
        }),
    )