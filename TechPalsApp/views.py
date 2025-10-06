from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages  # for flash messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.db import models
from django.contrib.auth.decorators import login_required, user_passes_test
from . models import Profile, Service, Group, GroupBooking, GroupMessage, GroupReport
from django.http import HttpResponseForbidden

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

def staff_required(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    return render(request, 'dashboard.admin.html')

@login_required
@user_passes_test(staff_required)
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
        tech_stack = request.POST.get('tech_stack')
        
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Username or Email already taken. Please choose another one!')
            return redirect('add-user')
        
        # Set user roles based on selection
        is_staff = role in ['admin', 'staff']
        is_superuser = role == 'admin'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        Profile.objects.update_or_create(user=user, defaults={'tech_stack': tech_stack})
        
        return redirect('users')
    return render(request, 'user.add.html')

@login_required
@user_passes_test(admin_required)
def users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    
    admins = users.filter(is_superuser=True)
    staff = users.filter(is_staff=True, is_superuser=False)
    regular_users = users.filter(is_staff=False, is_superuser=False)
    
    context = {
        'admins': admins,
        'staff': staff,
        'regular_users': regular_users,
    }
    
    return render(request, 'users.html', context)

@login_required
@user_passes_test(admin_required)
def update_user(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        tech_stack = request.POST.get('tech_stack')
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
        tech_stack=tech_stack
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        # Update profile
        user.profile.tech_stack = tech_stack
        user.profile.save()
        
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

def get_base_template(user):
    if user.is_superuser:
        return 'base_admin.html'
    elif user.is_staff:
        return 'base_staff.html'
    else:
        return 'base_user.html'

# User Profile Management
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

# Services Management
@login_required
@user_passes_test(admin_required)
def add_service(request):
    
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        service_description = request.POST.get('service_description')
        service_price = request.POST.get('service_price')
        
        Service.objects.create(
            service_name=service_name,
            service_description=service_description,
            service_price=service_price
        )
        return redirect('service-list')
    
    return render(request, 'service.add.html')

@login_required
def services(request):
    services = Service.objects.all()
    user = request.user
    
    if user.is_authenticated and user.is_superuser:
        base_template = 'base_admin.html'
    elif user.is_authenticated and user.is_staff:
        base_template = 'base_staff.html'
    else:
        base_template = 'base_user.html'
        
    return render(request, 'services.html', {
        'services': services,
        'base_template': base_template,
        'user': user
    })

@login_required
@user_passes_test(admin_required)
def update_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.service_name = request.POST.get('service_name')
        service.service_description = request.POST.get('service_description')
        service_price = request.POST.get('service_price')
        
        # Convert price safely
        try:
            service.service_price = float(service_price)
        except (ValueError, TypeError):
            service.service_price = 0  # or handle error differently
        
        service.save()
        
        return redirect('service-list')
    return render(request, 'service.update.html', {'service': service})

@login_required
@user_passes_test(admin_required)
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, f'{service.service_name} deleted successfully')
    return redirect('service-list')

# Groups management
@login_required
@user_passes_test(admin_required)
def create_group(request):
    users = User.objects.filter(is_staff=True)
    base_template = get_base_template(request.user)

    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group_leader_id = request.POST.get('group_leader')
        group_member_ids = request.POST.getlist('members')

        if not group_name or not group_leader_id or not group_member_ids:
            return render(request, 'groups.create.html', {
                'users': users,
                'error': 'Please fill all fields.',
                'base_template': base_template
            })

        group_leader = get_object_or_404(User, id=group_leader_id)
        members = User.objects.filter(id__in=group_member_ids)

        group = Group.objects.create(group_name=group_name, group_leader=group_leader)
        group.group_members.set(members)
        group.save()

        return redirect('group-list')

    return render(request, 'groups.create.html', {
        'users': users,
        'base_template': base_template
    })

@login_required
def group_list(request):
    base_template = get_base_template(request.user)

    # Show groups where user is a member or leader 
    # Admin can view all groups
    if request.user.is_superuser:
        groups = Group.objects.all()
    else:
        groups = Group.objects.filter(
        models.Q(group_members=request.user) | models.Q(group_leader=request.user)
    ).distinct()

    return render(request, 'group_list.html', {
        'groups': groups,
        'base_template': base_template
    })

@login_required
def group_chat(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    base_template = get_base_template(request.user)

    # Check if user is group leader or member
    if request.user != group.group_leader and request.user not in group.group_members.all():
        return HttpResponseForbidden("You are not a member of this group.")

    # Get messages ordered by timestamp
    messages = group.messages.order_by('timestamp')  # Assuming related_name='messages' on GroupMessage

    # Get the first group booking (if any)
    group_booking = group.group_bookings.first()  # Assuming related_name='group_bookings'

    # Get the report associated with the booking (if exists)
    group_report = getattr(group_booking, 'groupreport', None) if group_booking else None

    context = {
        'group': group,
        'group_booking': group_booking,
        'group_report': group_report,
        'messages': messages,
        'user': request.user,
        'base_template': base_template,
    }

    return render(request, 'group_chat.html', context)

# @login_required
# def group_detail(request, group_id):
#     group = get_object_or_404(Group, id=group_id)
#     base_template = get_base_template(request.user)

#     if request.user != group.group_leader and request.user not in group.group_members.all():
#         return HttpResponseForbidden("You are not a member of this group.")

#     messages = group.messages.order_by('timestamp')  # Assuming GroupMessage related_name is 'messages'
#     group_booking = group.group_bookings.first()  # Correct related_name
#     group_report = None
#     if group_booking:
#         group_report = getattr(group_booking, 'groupreport', None)

#     group_booking = group.group_bookings.first()

#     context = {
#         'group': group,
#         'group_booking': group_booking,
#         'group_report': group_report,
#         'messages': messages,
#         'user': request.user,
#         'base_template': base_template,
#     }
#     return render(request, 'group_detail.html', context)


@login_required
def post_group_message(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.group_members.all() and request.user != group.group_leader:
        return HttpResponseForbidden("You are not a member of this group.")

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        uploaded_file = request.FILES.get('file')

        if not content and not uploaded_file:
            # No message or file provided
            messages.error(request, "You must enter a message or attach a file.")
            return redirect('group-detail', group_id=group.id)

        message = GroupMessage.objects.create(
            group=group,
            sender=request.user,
            content=content,
            file=uploaded_file if uploaded_file else None,
        )

        return redirect('group-chat', group_id=group.id)
    else:
        return HttpResponseBadRequest("Invalid request method.")



@login_required
def submit_group_report(request, group_booking_id):
    group_booking = get_object_or_404(GroupBooking, id=group_booking_id)
    group = group_booking.group
    base_template = get_base_template(request.user)

    if request.user != group.group_leader:
        return HttpResponseForbidden("Only the group leader can submit the report.")

    if request.method == 'POST':
        report_text = request.POST.get('report_text')
        if report_text:
            GroupReport.objects.create(group_booking=group_booking, submitted_by=request.user, report_text=report_text)
            return redirect('group-detail', group.id)

    return render(request, 'group_report.html', {
        'group': group,
        'base_template': base_template
    })

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.group_leader:
        return HttpResponseForbidden("Only the group leader can edit this group.")

    users = User.objects.filter(is_staff=True)
    base_template = get_base_template(request.user)

    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group_leader_id = request.POST.get('group_leader')
        group_member_ids = request.POST.getlist('group_members')

        if not group_name or not group_leader_id or not group_member_ids:
            return render(request, 'groups/edit_group.html', {
                'group': group,
                'users': users,
                'error': 'Please fill all fields.',
                'base_template': base_template
            })

        new_leader = get_object_or_404(User, id=group_leader_id)
        members = User.objects.filter(id__in=group_member_ids)

        group.group_name = group_name
        group.group_leader = new_leader
        group.group_members.set(members)
        group.save()

        return redirect('group-list', group_id=group.id)

    return render(request, 'group_edit.html', {
        'group': group,
        'users': users,
        'base_template': base_template
    })
    
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect('group-list')
