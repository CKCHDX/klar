#!/usr/bin/env python3
"""
KSE Control Center - Example Usage
Demonstrates how to use the Control Center modules
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_standalone_module():
    """Example: Running a single module standalone"""
    from PyQt6.QtWidgets import QApplication
    from gui.control_center.control_center_api_client import ControlCenterAPIClient
    from gui.control_center.modules import PCCPrimaryControl
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create API client
    api_client = ControlCenterAPIClient()
    api_client.start_health_monitoring()
    
    # Create module
    pcc = PCCPrimaryControl(api_client)
    pcc.setWindowTitle("KSE Primary Control Center")
    pcc.resize(1200, 800)
    pcc.show()
    
    logger.info("Primary Control Center started")
    
    # Run application
    return app.exec()


def example_all_modules():
    """Example: Creating all modules in tabs"""
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
    from gui.control_center.control_center_api_client import ControlCenterAPIClient
    from gui.control_center.modules import (
        PCCPrimaryControl,
        MCSMainControlServer,
        SCSSystemStatus,
        ACCAuxiliaryControl,
        SCCSecondaryControl
    )
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create API client
    api_client = ControlCenterAPIClient()
    api_client.start_health_monitoring()
    
    # Create main window with tabs
    window = QMainWindow()
    window.setWindowTitle("KSE Control Center - All Modules")
    window.resize(1400, 900)
    
    # Create tab widget
    tabs = QTabWidget()
    
    # Add modules as tabs
    tabs.addTab(PCCPrimaryControl(api_client), "Primary Control")
    tabs.addTab(MCSMainControlServer(api_client), "Server Control")
    tabs.addTab(SCSSystemStatus(api_client), "System Status")
    tabs.addTab(ACCAuxiliaryControl(api_client), "Maintenance")
    tabs.addTab(SCCSecondaryControl(api_client), "Analytics")
    
    window.setCentralWidget(tabs)
    window.show()
    
    logger.info("All modules loaded in tabs")
    
    # Run application
    return app.exec()


def example_full_control_center():
    """Example: Running the complete Control Center"""
    from PyQt6.QtWidgets import QApplication
    from gui.control_center.control_center_main import ControlCenterMain
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create Control Center main window
    control_center = ControlCenterMain()
    control_center.show()
    
    logger.info("Full Control Center started")
    
    # Run application
    return app.exec()


def example_custom_integration():
    """Example: Custom integration with custom layout"""
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, 
        QVBoxLayout, QHBoxLayout, QPushButton
    )
    from gui.control_center.control_center_api_client import ControlCenterAPIClient
    from gui.control_center.modules import PCCPrimaryControl, MCSMainControlServer
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create API client
    api_client = ControlCenterAPIClient()
    api_client.start_health_monitoring()
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Custom Control Center Integration")
    window.resize(1600, 900)
    
    # Create central widget
    central = QWidget()
    layout = QHBoxLayout(central)
    
    # Add modules side-by-side
    pcc = PCCPrimaryControl(api_client)
    mcs = MCSMainControlServer(api_client)
    
    layout.addWidget(pcc)
    layout.addWidget(mcs)
    
    window.setCentralWidget(central)
    window.show()
    
    logger.info("Custom integration started")
    
    # Run application
    return app.exec()


def example_module_signals():
    """Example: Connecting to module signals"""
    from PyQt6.QtWidgets import QApplication
    from gui.control_center.control_center_api_client import ControlCenterAPIClient
    from gui.control_center.modules import PCCPrimaryControl
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create API client
    api_client = ControlCenterAPIClient()
    
    # Create module
    pcc = PCCPrimaryControl(api_client)
    
    # Connect to module signals
    pcc.refresh_requested.connect(
        lambda: logger.info("Refresh requested!")
    )
    
    # Connect to API client signals
    api_client.connection_status_changed.connect(
        lambda status: logger.info(f"Connection status: {status}")
    )
    
    api_client.health_check_completed.connect(
        lambda data: logger.info(f"Health check: {data.get('status', 'unknown')}")
    )
    
    api_client.error_occurred.connect(
        lambda error: logger.error(f"API error: {error}")
    )
    
    # Start monitoring
    api_client.start_health_monitoring()
    
    pcc.show()
    
    logger.info("Signal connections example started")
    
    # Run application
    return app.exec()


def example_programmatic_control():
    """Example: Programmatically controlling modules"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from gui.control_center.control_center_api_client import ControlCenterAPIClient
    from gui.control_center.modules import PCCPrimaryControl
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create API client and module
    api_client = ControlCenterAPIClient()
    pcc = PCCPrimaryControl(api_client)
    pcc.show()
    
    # Start monitoring
    api_client.start_health_monitoring()
    
    # Programmatically trigger refresh after 5 seconds
    def trigger_refresh():
        logger.info("Triggering programmatic refresh...")
        pcc.refresh_data()
    
    QTimer.singleShot(5000, trigger_refresh)
    
    # Stop updates after 30 seconds (for demo)
    def stop_updates():
        logger.info("Stopping updates...")
        pcc.stop_updates()
        api_client.stop_health_monitoring()
    
    QTimer.singleShot(30000, stop_updates)
    
    logger.info("Programmatic control example started")
    
    # Run application
    return app.exec()


def print_examples_menu():
    """Print available examples"""
    print("\n" + "="*60)
    print("KSE Control Center - Usage Examples")
    print("="*60)
    print("\nAvailable examples:")
    print("  1. Standalone Module       - Run a single module")
    print("  2. All Modules in Tabs     - All modules in tabbed interface")
    print("  3. Full Control Center     - Complete Control Center")
    print("  4. Custom Integration      - Custom layout example")
    print("  5. Module Signals          - Signal/slot connections")
    print("  6. Programmatic Control    - Programmatic module control")
    print("\nUsage:")
    print("  python example_control_center_usage.py [1-6]")
    print("\nExample:")
    print("  python example_control_center_usage.py 1")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print_examples_menu()
        return 0
    
    example_num = sys.argv[1]
    
    examples = {
        '1': ('Standalone Module', example_standalone_module),
        '2': ('All Modules in Tabs', example_all_modules),
        '3': ('Full Control Center', example_full_control_center),
        '4': ('Custom Integration', example_custom_integration),
        '5': ('Module Signals', example_module_signals),
        '6': ('Programmatic Control', example_programmatic_control),
    }
    
    if example_num not in examples:
        print(f"Error: Invalid example number: {example_num}")
        print_examples_menu()
        return 1
    
    name, func = examples[example_num]
    
    print("\n" + "="*60)
    print(f"Running Example: {name}")
    print("="*60 + "\n")
    
    try:
        return func()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Error running example: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
