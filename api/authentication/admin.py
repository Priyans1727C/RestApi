from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Extend the existing fieldsets to include the new fields
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'phone_number')}),
    )
    # Include fields on the add user page as well
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'phone_number')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
