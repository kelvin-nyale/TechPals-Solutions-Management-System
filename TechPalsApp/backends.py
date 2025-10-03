from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Custom backend trying to authenticate: {username}")
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            print("User not found by username or email")
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            print(f"Password valid for user: {user.username}")
            return user
        print("Password invalid")
        return None

