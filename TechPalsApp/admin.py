from django.contrib import admin
from .models import Group, GroupBooking, GroupMessage, GroupReport, Booking, Task, Post, Category

# Register your models here.
admin.site.register(Group)
admin.site.register(GroupBooking)
admin.site.register(GroupMessage)
admin.site.register(GroupReport)
admin.site.register(Booking)
admin.site.register(Task)
admin.site.register(Post)
admin.site.register(Category)
