from django.contrib import admin
from .models import Group, GroupBooking, GroupMessage, GroupReport

# Register your models here.
admin.site.register(Group)
admin.site.register(GroupBooking)
admin.site.register(GroupMessage)
admin.site.register(GroupReport)
