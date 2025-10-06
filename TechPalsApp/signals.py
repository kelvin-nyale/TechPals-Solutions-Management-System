from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile if new user
        Profile.objects.create(user=instance)
    else:
        # Update profile if exists
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            # If profile doesn't exist for some reason, create it
            Profile.objects.create(user=instance)

