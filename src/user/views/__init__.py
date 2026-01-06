from .login import LoginView
from .register import RegisterView
from .password import ForgotPasswordView, ResetPasswordView, ChangePasswordView
from .user import LogoutView, UserProfileView

__all__ = [
    "LoginView",
    "RegisterView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "ChangePasswordView",
    "LogoutView",
    "UserProfileView",
]
