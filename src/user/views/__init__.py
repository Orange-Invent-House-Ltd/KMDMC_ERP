from .login import LoginView
from .register import RegisterView
from .password import ForgotPasswordView, ResetPasswordView, ChangePasswordView
from .user import LogoutView
from .staff_profile import StaffProfileView, StaffTasksView, StaffCorrespondencesView

__all__ = [
    "LoginView",
    "RegisterView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "ChangePasswordView",
    "LogoutView",
    "UserProfileView",
    "StaffProfileView",
    "StaffTasksView",
    "StaffCorrespondencesView",
]
