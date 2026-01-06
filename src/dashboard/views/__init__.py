from .department import DepartmentViewSet
from .approval import ApprovalViewSet
from .task import TaskViewSet
from .correspondence import CorrespondenceViewSet
from .memo import MemoViewSet
from .dashboard import DashboardView

__all__ = [
    'DepartmentViewSet',
    'ApprovalViewSet',
    'TaskViewSet',
    'CorrespondenceViewSet',
    'MemoViewSet',
    'DashboardView',
]
