
"""
This file defines a set of Django context processors that make common data available globally to all templates:

1. get_vendor: Makes the current user's vendor object available in templates
2. get_user_profile: Makes the current user's profile object available in templates  
3. get_google_api: Makes Google API key from settings available in templates
4. get_paypal_client_id: Makes PayPal Client ID from settings available in templates

Context processors are registered in settings.py under TEMPLATES options, and their return values
are automatically merged into the context of every template rendered using a RequestContext.
This allows accessing these objects directly in any template without explicitly passing them from views.
"""

from urllib.parse import uses_relative  # Unused import, could be removed
from accounts.models import UserProfile  # Import UserProfile model
from vendor.models import Vendor  # Import Vendor model
from django.conf import settings  # Import Django settings module


def get_vendor(request):
    """
    Context processor that retrieves the vendor object for the current user.
    Makes the vendor object available in all templates.
    """
    try:
        # Try to get vendor object for current user
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None  # Set to None if user is not a vendor or not authenticated
    # Return dictionary that will be added to template context
    return dict(vendor=vendor)


def get_user_profile(request):
    """
    Context processor that retrieves the user profile for the current user.
    Makes the user profile object available in all templates.
    """
    try:
        # Try to get profile for current user
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None  # Set to None if profile doesn't exist or user not authenticated
    # Return dictionary for template context
    return dict(user_profile=user_profile)


def get_google_api(request):
    """
    Context processor that provides Google API key from settings.
    Makes the API key available in all templates.
    """
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}  # Return Google API key from settings


def get_paypal_client_id(request):
    """
    Context processor that provides PayPal Client ID from settings.
    Makes the Client ID available in all templates.
    """
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}  # Return PayPal Client ID from settings
