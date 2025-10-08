from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from TechPalsApp import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff-dashboard'),
    path('user/dashboard/', views.user_dashboard, name='user-dashboard'),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('users/add/', views.add_user, name='add-user'),
    path('users/', views.users, name='users'),
    path('user/update/<int:pk>/', views.update_user, name='update-user'),
    path('user/delete/<int:pk>/', views.delete_user, name='delete-user'),
    
    path('profile/update/', views.update_profile, name='profile_update'),
    
    path('services/add/', views.add_service, name='add-service'),
    path('services/', views.services, name='service-list'),
    path('services/update/<int:service_id>/', views.update_service, name='update-service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete-service'),
    
    path('bookings/', views.booking_list, name='booking-list'),
    path('bookings/add/', views.make_booking, name='make-booking'),
    path('booking/<int:booking_id>/update/', views.update_booking, name='update-booking'),
    path('booking/delete/<int:booking_id>/', views.delete_booking, name='delete-booking'),
    
    path('groups/', views.group_list, name='group-list'),  
    path('groups/create/', views.create_group, name='group-create'),
    path('groups/<int:group_id>/', views.group_chat, name='group-chat'),
    path('group/edit/<int:group_id>/', views.edit_group, name='group-edit'),
    # path('groups/<int:group_id>/edit/', views.edit_group, name='edit-group'),
    path('group/delete/<int:group_id>/', views.delete_group, name='group-delete'),
    path('groups/<int:group_id>/post_message/', views.post_group_message, name='post-group-message'),
    path('group-booking/<int:group_booking_id>/submit_report/', views.submit_group_report, name='submit-group-report'),
    
    # Tasks
    path('tasks/create/', views.create_task, name='create-task'),  # Admin only
    path('tasks/', views.staff_task_list, name='task-list'),       # Staff view their group's tasks
    path('tasks/<int:task_id>/edit/', views.update_task, name='edit-task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete-task'),
    
    #Blog posts management
    path('blog/', views.blog_list, name='blog-list'),
    path('blog/create/', views.create_post, name='create-post'),
    path('blog/category/<slug:slug>/', views.blog_category, name='blog-category'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog-detail'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)