
"""
This utility module provides essential functions for user management and notification:

1. detectUser: Routes users to appropriate dashboards based on their role (vendor, customer, or admin)

2. send_verification_email: Handles generating and sending verification emails with secure tokens
   for account activation and password reset functionality

3. send_notification: Generic email notification function supporting both single and multiple recipients
   using HTML templates

These functions centralize common operations used across the application for user management
and email communications, ensuring consistent behavior and reducing code duplication.
"""

from django.contrib import messages  # For flash messages
from django.contrib.sites.shortcuts import get_current_site  # To get current domain
from django.template.loader import render_to_string  # For rendering email templates
from django.utils.http import urlsafe_base64_encode  # For encoding user ID in URLs
from django.utils.encoding import force_bytes  # For preparing data for encoding
# For generating secure tokens
from django.contrib.auth.tokens import default_token_generator
# For email functionality ('message' import seems unused)
from django.core.mail import EmailMessage, message
from django.conf import settings  # For accessing settings like email configuration


def detectUser(user):
    """
    Determines the appropriate redirect URL based on user role.
    
    Args:
        user: The user object whose role is being checked
        
    Returns:
        String containing the redirect URL name or path
    """
    if user.role == 1:
        redirectUrl = 'vendorDashboard'  # Vendor role redirects to vendor dashboard
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'custDashboard'  # Customer role redirects to customer dashboard
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'  # Superadmin redirects to Django admin panel
        return redirectUrl


def send_verification_email(request, user, mail_subject, email_template):
    """
    Sends verification email with secure token for account activation or password reset.
    
    Args:
        request: The HTTP request object (needed for domain)
        user: The user to send verification to
        mail_subject: Subject line for the email
        email_template: Path to the email template
    """
    from_email = settings.DEFAULT_FROM_EMAIL  # Get sender email from settings
    current_site = get_current_site(request)  # Get current domain

    # Render email template with context containing token and user information
    message = render_to_string(email_template, {
        'user': user,  # Pass user object to template
        'domain': current_site,  # Pass domain for constructing verification URL
        # Encoded user ID for security
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        # Generate secure verification token
        'token': default_token_generator.make_token(user),
    })

    to_email = user.email  # Recipient is the user's email
    mail = EmailMessage(mail_subject, message, from_email,
                        to=[to_email])  # Create email message
    mail.content_subtype = "html"  # Set content type as HTML
    mail.send()  # Send the email


def send_notification(mail_subject, mail_template, context):
    """
    Generic function to send notification emails using HTML templates.
    
    Args:
        mail_subject: Subject line for the email
        mail_template: Path to the email template
        context: Dictionary containing template variables and recipient info
    """
    from_email = settings.DEFAULT_FROM_EMAIL  # Get sender email from settings
    # Render email content from template
    message = render_to_string(mail_template, context)

    # Handle both single email as string or multiple emails as list
    if (isinstance(context['to_email'], str)):
        to_email = []
        # Convert single email string to list
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']  # Use existing list of emails

    mail = EmailMessage(mail_subject, message, from_email,
                        to=to_email)  # Create email message
    mail.content_subtype = "html"  # Set content type as HTML
    mail.send()  # Send the email
