"""
KSE GUI Main - Main GUI application for Klar Search Engine
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kse.core.kse_config import ConfigManager
from gui.setup_wizard.setup_wizard_main import SetupWizard

logger = logging.getLogger(__name__)


class KSEMainGUI:
    """
    Main GUI Application for Klar Search Engine
    """
    
    def __init__(self):
        """Initialize the main GUI"""
        self.root = tk.Tk()
        self.root.title("Klar Search Engine")
        
        # Load configuration
        self.config = ConfigManager()
        
        # Set window size from config
        width = self.config.get('gui.width', 1200)
        height = self.config.get('gui.height', 700)
        self.root.geometry(f"{width}x{height}")
        
        # Check if first run
        config_path = Path(project_root) / 'config' / 'kse_config.json'
        if not config_path.exists():
            logger.info("First run detected, launching setup wizard")
            self._run_setup_wizard()
        
        # Create UI
        self._create_ui()
        
        logger.info("KSE Main GUI initialized")
    
    def _run_setup_wizard(self) -> None:
        """Run the setup wizard for first-time setup"""
        wizard = SetupWizard(self.root)
        # Make the wizard modal and wait for it to complete
        wizard.root.transient(self.root)
        wizard.root.grab_set()
        self.root.wait_window(wizard.root)
        
        if not wizard.completed:
            logger.warning("Setup wizard was not completed")
            if messagebox.askyesno(
                "Setup Incomplete",
                "Setup was not completed. Do you want to continue anyway?"
            ):
                # Reload config in case partial settings were saved
                self.config = ConfigManager()
            else:
                logger.info("User chose to exit after incomplete setup")
                sys.exit(0)
    
    def _create_ui(self) -> None:
        """Create the main UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔍 Klar Search Engine",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Info label
        app_name = self.config.get('app_name', 'Klar Search Engine')
        version = self.config.get('version', '4.0')
        info_label = ttk.Label(
            main_frame,
            text=f"{app_name} v{version}",
            font=("Arial", 12)
        )
        info_label.pack(pady=(0, 30))
        
        # Content area
        content_frame = ttk.LabelFrame(main_frame, text="Main Controls", padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder content
        ttk.Label(
            content_frame,
            text="Welcome to Klar Search Engine!\n\nThe GUI is ready to use.",
            justify=tk.CENTER,
            font=("Arial", 11)
        ).pack(expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _show_settings(self) -> None:
        """Show settings dialog"""
        messagebox.showinfo(
            "Settings",
            "Settings dialog will be implemented here.\n\n"
            "For now, you can edit the configuration file directly:\n"
            f"{self.config.config_path}"
        )
    
    def _show_about(self) -> None:
        """Show about dialog"""
        app_name = self.config.get('app_name', 'Klar Search Engine')
        version = self.config.get('version', '4.0')
        
        messagebox.showinfo(
            "About",
            f"{app_name}\nVersion {version}\n\n"
            "A modern search engine with hierarchical keywords\n"
            "and metadata-based search capabilities."
        )
    
    def _exit(self) -> None:
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            logger.info("Application closing")
            self.root.quit()
    
    def run(self) -> None:
        """Run the main GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Klar Search Engine GUI")
    
    try:
        app = KSEMainGUI()
        app.run()
    except Exception as e:
        logger.error(f"Error running GUI: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to start GUI: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
