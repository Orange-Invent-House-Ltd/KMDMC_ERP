from django.urls import path

from user.views.login import LoginView
from user.views.register import RegisterView
from user.views.password import (
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)
from user.views.user import LogoutView, UserProfileView
from user.views.staff_profile import (
    StaffProfileView,
    StaffTasksView,
    StaffCorrespondencesView,
)

app_name = "user"

urlpatterns = [
    # Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Password management
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    
    # Profile
    path("profile/", UserProfileView.as_view(), name="profile"),
    
    # Staff Profile
    path("me/", StaffProfileView.as_view(), name="staff_profile"),
    path("me/tasks/", StaffTasksView.as_view(), name="staff_tasks"),
    path("me/correspondences/", StaffCorrespondencesView.as_view(), name="staff_correspondences"),
]
