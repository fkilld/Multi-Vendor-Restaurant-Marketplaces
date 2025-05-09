# Admin Configuration Flow:
# 1. Import necessary modules from Django
# 2. Define a custom UserAdmin class to customize the admin interface for User model
# 3. Register the User model with our CustomUserAdmin
# 4. Register the UserProfile model with the default admin interface

# Import the admin module from Django to use its functionality for registering models
from django.contrib import admin
# Import User and UserProfile models from the local models.py file
from .models import User, UserProfile
# Import the built-in UserAdmin class that we'll extend for our custom implementation
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Customize which fields appear in the list view of users in admin panel
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    # Set the default ordering of users to show newest users first
    ordering = ('-date_joined',)
    # Disable the horizontal filter widget for many-to-many fields (empty for default behavior)
    filter_horizontal = ()
    # Disable the right sidebar filter options (empty for default behavior)
    list_filter = ()
    # Disable the default fieldsets for user detail view (empty for default behavior)
    fieldsets = ()

# Register the User model with our CustomUserAdmin configuration
admin.site.register(User, CustomUserAdmin)
# Register the UserProfile model with the default admin interface
admin.site.register(UserProfile)