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
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)