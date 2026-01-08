from .login import LoginSerializer, LoginResponseSerializer
from .register import RegisterSerializer
from .password import ForgotPasswordSerializer, ResetPasswordSerializer
from .user import UserSerializer
from .staff_profile import (
    DepartmentSerializer,
    DepartmentDropdownSerializer,
    StaffListSerializer,
    StaffProfileSerializer,
    StaffProfileUpdateSerializer,
    StaffTaskSerializer,
    StaffActivitySerializer,
    PerformanceRecordSerializer,
)

__all__ = [
    "LoginSerializer",
    "LoginResponseSerializer",
    "RegisterSerializer",
    "ForgotPasswordSerializer",
    "ResetPasswordSerializer",
    "UserSerializer",
    # Staff Profile
    "DepartmentSerializer",
    "DepartmentDropdownSerializer",
    "StaffListSerializer",
    "StaffProfileSerializer",
    "StaffProfileUpdateSerializer",
    "StaffTaskSerializer",
    "StaffActivitySerializer",
    "PerformanceRecordSerializer",
]
