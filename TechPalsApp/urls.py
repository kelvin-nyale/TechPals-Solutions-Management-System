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
    
    path('groups/', views.group_list, name='group-list'),  # You might want to add this view
    path('groups/create/', views.create_group, name='group-create'),
    path('groups/<int:group_id>/', views.group_chat, name='group-chat'),
    path('group/edit/<int:group_id>/', views.edit_group, name='group-edit'),
    path('group/delete/<int:group_id>/', views.delete_group, name='group-delete'),
    path('groups/<int:group_id>/post_message/', views.post_group_message, name='post-group-message'),
    path('group-booking/<int:group_booking_id>/submit_report/', views.submit_group_report, name='submit-group-report'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)