
"""
This code implements a custom user authentication system with the following components:

1. UserManager: A custom manager extending BaseUserManager to handle user creation operations 
   for both regular users and superusers, enforcing requirements like email and username.

2. User: A custom user model extending AbstractBaseUser with role-based authentication 
   (Vendor/Customer) and standard authentication fields.

3. UserProfile: An extension model connected to User via OneToOneField, storing user's 
   personal details, address information, and geographical coordinates using GeoDjango.

The system allows for different user roles with different permissions, and stores 
location data using Django's GIS capabilities for geo-spatial features.
"""

from django.db import models  # Core Django model functionality
# Base classes for custom user authentication
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Relationship field types
from django.db.models.fields.related import ForeignKey, OneToOneField

# GeoDjango model capabilities for geographic data
from django.contrib.gis.db import models as gismodels
# GeoDjango Point object for storing coordinates
from django.contrib.gis.geos import Point


class UserManager(BaseUserManager):
    # Custom manager class that handles user creation with email as primary identifier
    def create_user(self, first_name, last_name, username, email, password=None):
        # Method to create regular users with validation
        if not email:
            # Email validation
            raise ValueError('User must have an email address')

        if not username:
            # Username validation
            raise ValueError('User must have an username')

        user = self.model(
            # Normalizing email (lowercase domain part)
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )  # Create user instance with provided details
        user.set_password(password)  # Hash the password for security
        user.save(using=self._db)  # Save user to database
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        # Method to create admin users with all privileges
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )  # Create regular user first
        # Set admin privileges
        user.is_admin = True  # Admin status
        user.is_active = True  # Account active by default
        user.is_staff = True  # Staff access to admin panel
        user.is_superadmin = True  # Superadmin privileges
        user.save(using=self._db)  # Save with admin privileges
        return user


class User(AbstractBaseUser):
    # Custom user model with role-based authentication
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),  # Role for restaurant/food vendors
        (CUSTOMER, 'Customer'),  # Role for customers ordering food
    )
    # Basic user information fields
    first_name = models.CharField(max_length=50)  # User's first name
    last_name = models.CharField(max_length=50)  # User's last name
    username = models.CharField(max_length=50, unique=True)  # Unique username
    # Unique email - used for login
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(
        max_length=12, blank=True)  # Optional phone number
    role = models.PositiveSmallIntegerField(
        # User role (vendor/customer)
        choices=ROLE_CHOICE, blank=True, null=True)

    # Required fields for Django authentication system
    date_joined = models.DateTimeField(
        auto_now_add=True)  # Account creation timestamp
    last_login = models.DateTimeField(
        auto_now_add=True)  # Last login timestamp
    # Creation timestamp (redundant with date_joined)
    created_date = models.DateTimeField(auto_now_add=True)
    # Auto-updated modification timestamp
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)  # Admin status flag
    # Staff status for admin site access
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Account activation status
    is_superadmin = models.BooleanField(
        default=False)  # Superadmin privileges flag

    USERNAME_FIELD = 'email'  # Field used for authentication (login)
    # Required fields when creating user
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()  # Assign custom manager to user model

    def __str__(self):
        return self.email  # String representation of user

    def has_perm(self, perm, obj=None):
        return self.is_admin  # Permission check - admins have all permissions

    def has_module_perms(self, app_label):
        return True  # Module permission check - users have access to all modules

    def get_role(self):
        # Helper method to get text representation of user role
        if self.role == 1:
            user_role = 'Vendor'
        elif self.role == 2:
            user_role = 'Customer'
        return user_role  # Return role name


class UserProfile(models.Model):
    # Extended user profile with additional details and location information
    user = OneToOneField(User, on_delete=models.CASCADE,
                         blank=True, null=True)  # Link to User model
    profile_picture = models.ImageField(
        upload_to='users/profile_pictures', blank=True, null=True)  # User profile image
    cover_photo = models.ImageField(
        upload_to='users/cover_photos', blank=True, null=True)  # Profile cover image

    # Address information
    address = models.CharField(
        max_length=250, blank=True, null=True)  # Street address
    country = models.CharField(max_length=15, blank=True, null=True)  # Country
    state = models.CharField(max_length=15, blank=True,
                             null=True)  # State/province
    city = models.CharField(max_length=15, blank=True, null=True)  # City
    pin_code = models.CharField(
        max_length=6, blank=True, null=True)  # Postal/ZIP code

    # Geographic coordinates
    latitude = models.CharField(
        max_length=20, blank=True, null=True)  # Latitude as string
    longitude = models.CharField(
        max_length=20, blank=True, null=True)  # Longitude as string
    # GeoDjango point field (WGS84 coordinate system)
    location = gismodels.PointField(blank=True, null=True, srid=4326)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    # Auto-updated modification timestamp
    modified_at = models.DateTimeField(auto_now=True)

    # Commented-out method for full address formatting
    # def full_address(self):
    #     return f'{self.address_line_1}, {self.address_line_2}'

    def __str__(self):
        return self.user.email  # String representation using linked user's email

    def save(self, *args, **kwargs):
        # Override save method to automatically create Point object from lat/long
        if self.latitude and self.longitude:
            # Create Point object from string coordinates
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        # Normal save if no coordinates
        return super(UserProfile, self).save(*args, **kwargs)
