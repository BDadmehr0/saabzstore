from django.urls import path

from . import views

urlpatterns = [
    path("auth/", views.multi_step_auth, name="multi_step_auth"),
    path("api/send-otp/", views.api_send_otp, name="api_send_otp"),
    path("api/verify-otp/", views.api_verify_otp, name="api_verify_otp"),
    path("api/set-password/", views.api_set_password, name="api_set_password"),
    path("api/set-name/", views.api_set_name, name="api_set_name"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="logout"),
]
