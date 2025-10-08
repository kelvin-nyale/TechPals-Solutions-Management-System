from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date
from django.utils import timezone
from django.utils.text import slugify


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

# class Booking(models.Model):
#     booking_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     booking_service = models.ForeignKey('Service', on_delete=models.CASCADE)
#     due_date = models.DateField(default=date.today)  # default added here

#     def __str__(self):
#         return f"Booking for {self.booking_service.service_name} by {self.booking_user.username}"

#     def clean(self):
#         super().clean()
#         if self.due_date < date.today():
#             raise ValidationError("Due date cannot be in the past.")
class Booking(models.Model):
    booking_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booking_service = models.ForeignKey('Service', on_delete=models.CASCADE)
    due_date = models.DateField()

    def __str__(self):
        return f"Booking for {self.booking_service.service_name} by {self.booking_user.username}"


# class Task(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     due_date = models.DateField()
#     booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='tasks')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} for {self.booking.booking_service.service_name}"

#     @property
#     def group(self):
#         try:
#             return self.booking.groupbooking.group
#         except GroupBooking.DoesNotExist:
#             return None
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.booking.booking_service.service_name}"

    # @property
    # def group(self):
    #     # Return group assigned via GroupBooking if exists
    #     return getattr(self.booking, 'group_booking', None) and self.booking.group_booking.group
    
    @property
    def group(self):
        if hasattr(self.booking, 'group_booking'):
            return self.booking.group_booking.group
        return None



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


# class GroupBooking(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_bookings')
#     booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
#     due_date = models.DateField()

#     def __str__(self):
#         return f"{self.booking.booking_service.service_name} assigned to {self.group.group_name}"
class GroupBooking(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_bookings')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='group_booking')
    due_date = models.DateField()

    def __str__(self):
        return f"{self.booking} assigned to {self.group.group_name}"

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

## Blog posts management
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:150]  # first 150 chars as excerpt
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title