
"""
The Vendor model represents a vendor entity linked to a user and user profile. It stores vendor details such as name, slug, license image, approval status, and timestamps for creation and modification.

The Vendor model includes a method is_open() to check if the vendor is currently open based on today's day and the current time compared to the vendor's opening hours stored in the OpeningHour model.

The save() method is overridden to send notification emails to the vendor's user when the approval status changes.

The OpeningHour model stores the opening hours for each vendor for each day of the week, including whether the vendor is closed on that day/time.

The models use choices for days of the week and half-hour time slots in 12-hour format with AM/PM.

The OpeningHour model enforces unique constraints on vendor, day, from_hour, and to_hour to avoid overlapping or duplicate time slots.
"""

# Import required modules
from enum import unique  # For creating unique enumerations
from django.db import models  # Django's ORM functionality
from accounts.models import User, UserProfile  # User-related models
from accounts.utils import send_notification  # Utility function to send emails
from datetime import time, date, datetime  # Date and time handling


class Vendor(models.Model):
    # Vendor model links to User and UserProfile with one-to-one relationships
    # Link to authentication user
    user = models.OneToOneField(
        User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name='userprofile', on_delete=models.CASCADE)  # Link to user profile
    # Store vendor/restaurant name
    vendor_name = models.CharField(max_length=50)
    # URL-friendly unique identifier
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(
        upload_to='vendor/license')  # Store license document image
    # Approval status - defaults to unapproved
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True)  # Timestamp for creation
    # Auto-updated timestamp for modifications
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name  # String representation for admin panel and debugging

    def is_open(self):
        # Check if vendor is currently open based on day and time
        today_date = date.today()
        today = today_date.isoweekday()  # Get day number (1-7) for current day

        current_opening_hours = OpeningHour.objects.filter(
            vendor=self, day=today)  # Query opening hours for today
        now = datetime.now()
        # Format current time as string for comparison
        current_time = now.strftime("%H:%M:%S")

        is_open = None  # Default status until determined
        for i in current_opening_hours:
            if not i.is_closed:  # Skip closed time slots
                # Convert stored time strings to comparable datetime objects
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                # Check if current time falls between opening and closing times
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        # Return open status (True, False, or None if no hours defined)
        return is_open

    def save(self, *args, **kwargs):
        # Override save method to handle approval notifications
        # Check if this is an update (not a new record)
        if self.pk is not None:
            orig = Vendor.objects.get(pk=self.pk)  # Get original record
            if orig.is_approved != self.is_approved:  # Detect approval status change
                mail_template = 'accounts/emails/admin_approval_email.html'  # Email template path
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }  # Prepare context data for email template
                if self.is_approved == True:
                    # Send approval notification
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send rejection notification
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, mail_template, context)
        # Call parent save method
        return super(Vendor, self).save(*args, **kwargs)


# Define days of week as choices for the OpeningHour model
DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

# Generate time choices in half-hour increments with 12-hour format
HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(
    h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE)  # Link to vendor
    day = models.IntegerField(choices=DAYS)  # Day of week (1-7)
    from_hour = models.CharField(
        choices=HOUR_OF_DAY_24, max_length=10, blank=True)  # Opening time
    to_hour = models.CharField(
        choices=HOUR_OF_DAY_24, max_length=10, blank=True)  # Closing time
    is_closed = models.BooleanField(default=False)  # Flag for closed days

    class Meta:
        # Default ordering by day and reverse start time
        ordering = ('day', '-from_hour')
        # Prevent duplicate/overlapping hours
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()  # Return day name for display
