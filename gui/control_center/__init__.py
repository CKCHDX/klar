"""
KSE Control Center
Main control interface for KSE system management
"""

__all__ = [
    'ControlCenterMain',
    'ControlCenterConfig',
    'ControlCenterNavigation',
    'ControlCenterAPIClient',
]

def __getattr__(name):
    """Lazy import to avoid loading PyQt6 unless needed"""
    if name == 'ControlCenterMain':
        from gui.control_center.control_center_main import ControlCenterMain
        return ControlCenterMain
    elif name == 'ControlCenterConfig':
        from gui.control_center.control_center_config import ControlCenterConfig
        return ControlCenterConfig
    elif name == 'ControlCenterNavigation':
        from gui.control_center.control_center_navigation import ControlCenterNavigation
        return ControlCenterNavigation
    elif name == 'ControlCenterAPIClient':
        from gui.control_center.control_center_api_client import ControlCenterAPIClient
        return ControlCenterAPIClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
