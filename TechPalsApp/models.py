from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# from bookings.models import Booking  # Adjust import path if needed
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    tech_stack = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
class Service(models.Model):
    service_name = models.CharField(max_length=100)
    service_description = models.TextField()
    service_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.service_name} - {self.service_price}"
    

User = settings.AUTH_USER_MODEL

class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    # Add any other fields you need

    def __str__(self):
        return f"Booking for {self.service.name}"


# class Group(models.Model):
#     group_name = models.CharField(max_length=100)
#     group_members = models.ManyToManyField(User, limit_choices_to={'role': 'staff'}, related_name='custom_groups')
#     group_leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'staff'}, related_name='led_groups')

#     def __str__(self):
#         return self.group_name
class Group(models.Model):
    group_name = models.CharField(max_length=100)
    group_members = models.ManyToManyField(User, related_name='custom_groups')
    group_leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True},  # Only staff can be leader
        related_name='led_groups'
    )

    def __str__(self):
        return self.group_name



class GroupBooking(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_bookings')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.booking.service.name} assigned to {self.group.group_name}"


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='group_messages_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender} in {self.group}"


class GroupReport(models.Model):
    group_booking = models.OneToOneField(GroupBooking, on_delete=models.CASCADE)
    report_text = models.TextField()
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'staff'}
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.group_booking.booking.service.name} by {self.submitted_by.username if self.submitted_by else 'Unknown'}"
