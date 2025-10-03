from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages  # for flash messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from . models import Profile

# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        # profile = request.POST.get('profile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            # profile=profile,
            password=password
        )
        messages.success(request, 'User created successfully')
        return redirect('login')
    
    return render(request, 'register.html')


# def login_view(request):
#     if request.method == 'POST':
#         identifier = request.POST.get('identifier')  # could be username or email
#         password = request.POST.get('password')
        
#         print(f"Received identifier: {identifier}")
#         print(f"Received password: {'*' * len(password) if password else None}")

#         user = None
#         # Try to find a user matching the identifier
#         try:
#             user = User.objects.get(Q(username=identifier) | Q(email=identifier))
#             print(f"User found: {user.username}")
#             user = authenticate(request, username=user.username, password=password)
#             print(f"Authentication success: {user is not None}")
#         except User.DoesNotExist:
#             print("User does not exist.")
#             user = None

#         if user is not None:
#             login(request, user)
#             messages.success(request, f"Welcome Back {user.username}")
#             # Role-based redirection
#             if user.is_superuser:
#                 return redirect('admin-dashboard')
#             elif user.is_staff:
#                 return redirect('staff-dashboard')
#             else:
#                 return redirect('user-dashboard')
            
#         else:
#             messages.error(request, 'Invalid Credentials.')
        
        
#     return render(request, 'login.html')
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # username or email
        password = request.POST.get('password')
        
        print(f"Received identifier: {identifier}")
        print(f"Received password: {'*' * len(password) if password else None}")

        user = None

        try:
            # Fetch user by username OR email

            # Now attempt to authenticate
            user = authenticate(request, username=identifier, password=password)
            print(f"Authentication success: {user is not None}")

        except User.DoesNotExist:
            print("User does not exist.")
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome Back {user.username}")
            # Role-based redirection
            if user.is_superuser:
                return redirect('admin-dashboard')
            elif user.is_staff:
                return redirect('staff-dashboard')
            else:
                return redirect('user-dashboard')
        else:
            messages.error(request, 'Wrong password  or username/email.')
    
    return render(request, 'login.html')

def admin_required(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    return render(request, 'dashboard.admin.html')

@login_required
def staff_dashboard(request):
    return render(request, 'dashboard.staff.html')

@login_required
def user_dashboard(request):
    return render(request, 'dashboard.user.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')

# User management views
@login_required
@user_passes_test(admin_required)
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Username or Email already taken. Please choose another one!')
            return redirect('add-user')
        
        # Set user roles based on selection
        is_staff = role in ['admin', 'staff']
        is_superuser = role == 'admin'
        
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return redirect('users')
    return render(request, 'user.add.html')

@login_required
@user_passes_test(admin_required)
def users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users.html', {'users': users})

@login_required
@user_passes_test(admin_required)
def update_user(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Check if username or email is already taken (excluding current user)
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Username already exists')
            return redirect('update-user')
        
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email already exists')
            return redirect('update-user')
        
        user.username= username
        user.email= email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        messages.success(request, 'User updated successfully')
        return redirect('users')
    
    return render(request, 'user.update.html', {'user': user})

# using POST method to delete. it requires a form with post method
# @login_required
# @user_passes_test(admin_required)
# def delete_user(request, pk):
#     user = get_object_or_404(User, id=pk)

#     if request.method == 'POST':
#         user.delete()
#         messages.success(request, f'User {user.username} deleted successfully')
#         return redirect('users')
    
#     return render(request, 'delete-user.html')

    
# using get method to handle deletions
@login_required
@user_passes_test(admin_required)
def delete_user(request, pk):
    user = get_object_or_404(User, id=pk)
    user.delete()
    messages.success(request, f'User {user.username} deleted successfully')
    return redirect('users')

@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
            profile.save()
        # Redirect based on user role
        if request.user.is_superuser:
            return redirect('admin-dashboard')  
        elif request.user.is_staff:
            return redirect('staff-dashboard') 
        else:
            return redirect('user-dashboard') 

    # Determine base template based on role
    if request.user.is_superuser:
        base_template = 'base_admin.html'
    elif request.user.is_staff:
        base_template = 'base_staff.html'
    else:
        base_template = 'base_user.html'

    return render(request, 'profile_update.html', {
        'profile': profile,
        'base_template': base_template,
    })