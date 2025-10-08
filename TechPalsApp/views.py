from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages  # for flash messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.db import models
from django.contrib.auth.decorators import login_required, user_passes_test
from . models import Profile, Service, Group, GroupBooking, GroupMessage, GroupReport, Booking, Task, Post, Category
from django.http import HttpResponseForbidden
from datetime import datetime, date
from django.core.paginator import Paginator
from .forms import PostForm, ContactForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

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

# @login_required
def services(request):
    services = Service.objects.all()
    user = request.user
    
    if user.is_authenticated and user.is_superuser:
        base_template = 'base_admin.html'
    elif user.is_authenticated and user.is_staff:
        base_template = 'base_staff.html'
    elif user.is_authenticated and not user.is_staff:
        base_template = 'base_user.html'
    else:
        base_template = 'base.html'
        
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

# Bookings management

@login_required
def make_booking(request):
    # Determine base_template based on user role
    if request.user.is_superuser:
        base_template = 'base_admin.html'
    elif request.user.is_staff:
        base_template = 'base_staff.html'
    else:
        base_template = 'base_user.html'

    if request.method == 'POST':
        booking_user_id = request.POST.get('booking_user') if request.user.is_superuser else request.user.id
        booking_service_id = request.POST.get('booking_service')
        due_date_str = request.POST.get('due_date')

        # Convert due_date string to date object
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid due date format.")
            return _render_booking_form(request, base_template, due_date_str, booking_service_id, booking_user_id)

        # Validate due date is not today or in the past
        if due_date <= date.today():
            messages.error(request, "Due date cannot be today or in the past.")
            return _render_booking_form(request, base_template, due_date_str, booking_service_id, booking_user_id)

        # Get user and service objects
        try:
            booking_user = User.objects.get(id=booking_user_id)
            booking_service = Service.objects.get(id=booking_service_id)
        except (User.DoesNotExist, Service.DoesNotExist):
            messages.error(request, "Invalid user or service selected.")
            return redirect('make_booking')  # update URL name if needed

        # Save the booking
        booking = Booking(
            booking_user=booking_user,
            booking_service=booking_service,
            due_date=due_date
        )
        try:
            booking.full_clean()
            booking.save()
        except ValidationError as e:
            messages.error(request, e.message_dict)
            return _render_booking_form(request, base_template, due_date_str, booking_service_id, booking_user_id)

        messages.success(request, "Booking created successfully.")
        return redirect('booking-list')  # update URL name if needed

    # GET request: render form with defaults
    booking_user_id = request.user.id if not request.user.is_superuser else None
    return _render_booking_form(request, base_template, '', None, booking_user_id)


def _render_booking_form(request, base_template, input_due_date, selected_service_id, selected_user_id):
    context = {
        'input_due_date': input_due_date,
        'selected_service_id': selected_service_id,
        'base_template': base_template,
        'services': Service.objects.all(),
    }
    if request.user.is_superuser:
        context['users'] = User.objects.all()
        context['selected_user_id'] = selected_user_id

    return render(request, 'booking.make.html', context)


@login_required
def booking_list(request):
    user = request.user

    if user.is_superuser or user.is_staff:
        # Admin and staff see all bookings
        bookings = Booking.objects.all()
    else:
        # Normal users see only their own bookings
        bookings = Booking.objects.filter(booking_user=user)

    if user.is_superuser:
        base_template = 'base_admin.html'
    elif user.is_staff:
        base_template = 'base_staff.html'
    else:
        base_template = 'base_user.html'

    return render(request, 'bookings.html', {
        'bookings': bookings,
        'base_template': base_template,
        'user_role': 'admin' if user.is_superuser else 'staff' if user.is_staff else 'user'
    })


@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Permissions check
    if not request.user.is_superuser and request.user != booking.booking_user:
        messages.error(request, "You do not have permission to update this booking.")
        return redirect('booking-list')

    # Determine base template
    if request.user.is_superuser:
        base_template = 'base_admin.html'
    elif request.user.is_staff:
        base_template = 'base_staff.html'
    else:
        base_template = 'base_user.html'

    # defining local variable before using it
    def render_update_form(error=None):
        return render(request, 'booking.update.html', {
            'booking': booking,
            'services': Service.objects.all(),
            'users': User.objects.all(),
            'base_template': base_template,
            'error': error
        })

    if request.method == 'POST':
        booking_service_id = request.POST.get('booking_service')
        due_date_str = request.POST.get('due_date')

        # Admin can change user
        if request.user.is_superuser:
            booking_user_id = request.POST.get('booking_user')
            try:
                booking.booking_user = User.objects.get(id=booking_user_id)
            except User.DoesNotExist:
                return render_update_form("Invalid user.")

        try:
            booking.booking_service = Service.objects.get(id=booking_service_id)
        except Service.DoesNotExist:
            return render_update_form("Invalid service.")

        try:
            booking.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render_update_form("Invalid date format.")

        if booking.due_date <= date.today():
            return render_update_form("Due date cannot be today or in the past.")

        try:
            booking.full_clean()
            booking.save()
            messages.success(request, "Booking updated successfully.")
            return redirect('booking-list')
        except ValidationError as e:
            return render_update_form(e.message_dict)

    # If GET request, show form
    return render_update_form()


@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Staff cannot delete bookings.")
        return redirect('booking-list')
    if not request.user.is_superuser and booking.booking_user != request.user:
        messages.error(request, "You do not have permission to delete this booking.")
        return redirect('booking-list')

    booking.delete()
    messages.success(request, "Booking deleted successfully.")
    return redirect('booking-list')


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('booking-list')

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
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Only group leader or admin can edit
    if not (request.user == group.group_leader or request.user.is_superuser):
        messages.error(request, "You do not have permission to edit this group.")
        return redirect('group-detail', group_id)

    users = User.objects.all()

    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group_leader_id = request.POST.get('group_leader')
        group_member_ids = request.POST.getlist('group_members')

        # Update fields
        group.group_name = group_name

        try:
            group.group_leader = User.objects.get(id=group_leader_id)
        except User.DoesNotExist:
            messages.error(request, "Invalid leader selected.")
            return redirect('edit-group', group_id)

        group.save()
        group.group_members.set(group_member_ids)  # update many-to-many
        group.save()

        messages.success(request, "Group updated successfully.")
        if request.user.is_superuser:
            return redirect('group-list')  # Admins go to group list
        else:
            return redirect('group-chat', group_id)  # Others go to group chat

    base_template = (
        'base_admin.html' if request.user.is_superuser else
        'base_staff.html' if request.user.is_staff else
        'base_user.html'
    )

    return render(request, 'group_edit.html', {
        'group': group,
        'users': users,
        'base_template': base_template,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect('group-list')

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
@user_passes_test(lambda u: u.is_superuser)
def create_task(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking')
        group_id = request.POST.get('group')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date')

        # Validate booking and group
        try:
            booking = Booking.objects.get(id=booking_id)
            group = Group.objects.get(id=group_id)
        except (Booking.DoesNotExist, Group.DoesNotExist):
            messages.error(request, "Invalid booking or group selected.")
            return redirect('create-task')

        # Validate due date
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            messages.error(request, "Invalid due date format.")
            return redirect('create-task')

        if parsed_due_date < date.today():
            messages.error(request, "Due date cannot be in the past.")
            return redirect('create-task')

        # Create or update GroupBooking
        group_booking, created = GroupBooking.objects.get_or_create(
            booking=booking,
            defaults={'group': group, 'due_date': parsed_due_date}
        )
        if not created:
            group_booking.group = group
            group_booking.due_date = parsed_due_date
            group_booking.save()

        # Create Task
        Task.objects.create(
            title=title,
            description=description,
            due_date=parsed_due_date,
            booking=booking,
        )

        messages.success(request, "Task assigned successfully.")
        return redirect('task-list')

    else:
        # GET request, show all bookings and groups to assign
        bookings = Booking.objects.all()
        groups = Group.objects.all()

        return render(request, 'task_create.html', {
            'bookings': bookings,
            'groups': groups,
            'base_template': 'base_admin.html',
        })


@login_required
def staff_task_list(request):
    today = date.today()

    if request.user.is_superuser:
        # Admin sees all upcoming tasks
        tasks = Task.objects.filter(due_date__gte=today).order_by('due_date')
        base_template = 'base_admin.html'
    elif request.user.is_staff:
        # Staff see tasks assigned to their groups
        user_groups = request.user.custom_groups.all()
        tasks = Task.objects.filter(
            booking__group_booking__group__in=user_groups,
            due_date__gte=today
        ).distinct().order_by('due_date')
        base_template = 'base_staff.html'
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")

    return render(request, 'task_list.html', {
        'tasks': tasks,
        'base_template': base_template,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    bookings = Booking.objects.exclude(group__isnull=True)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date', '')
        booking_id = request.POST.get('booking')

        try:
            due_date_parsed = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid due date format.")
            return render(request, 'task.update.html', {
                'task': task, 'bookings': bookings, 'base_template': 'base_admin.html'
            })

        task.title = title
        task.description = description
        task.due_date = due_date_parsed
        task.booking = Booking.objects.get(id=booking_id)
        task.save()

        messages.success(request, "Task updated successfully.")
        return redirect('task-list')

    return render(request, 'tasks.update.html', {
        'task': task,
        'bookings': bookings,
        'base_template': 'base_admin.html',
    })

    
@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only admin can delete
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.save()
    return redirect('task-list', {'task': task})

## Blog posts management
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # request.FILES here
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('admin-dashboard')
    else:
        form = PostForm()

    base_template = 'base_admin.html' if request.user.is_superuser else 'base.html'

    return render(request, 'blog_post.html', {
        'form': form,
        'base_template': base_template,
    })


def blog_list(request):
    post_list = Post.objects.order_by('-published_date')
    paginator = Paginator(post_list, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    categories = Category.objects.all()
    recent_posts = Post.objects.order_by('-published_date')[:5]

    return render(request, 'blog_list.html', {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    })


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    categories = Category.objects.all()
    recent_posts = Post.objects.order_by('-published_date')[:5]

    return render(request, 'blog_detail.html', {
        'post': post,
        'categories': categories,
        'recent_posts': recent_posts,
    })


def blog_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    post_list = category.posts.order_by('-published_date')
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    categories = Category.objects.all()
    recent_posts = Post.objects.order_by('-published_date')[:5]

    return render(request, 'blog_list.html', {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'current_category': category,
    })
    
## Contact management
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # You can process the data, send email, save to DB, etc.
            messages.success(request, "Thanks for reaching out! We'll get back to you shortly.")
            return redirect('contact')  # redirects to the same page
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})