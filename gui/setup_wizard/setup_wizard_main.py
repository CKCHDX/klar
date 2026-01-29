"""
Setup Wizard Main - First-time setup for Klar Search Engine
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
from typing import Optional

from kse.core.kse_config import ConfigManager

logger = logging.getLogger(__name__)


class SetupWizard:
    """
    First-time setup wizard for Klar Search Engine
    
    Guides users through initial configuration and setup.
    """
    
    def __init__(self, parent: Optional[tk.Tk] = None):
        """
        Initialize the Setup Wizard
        
        Args:
            parent: Parent Tkinter window, or None to create a new one
        """
        if parent is None:
            self.root = tk.Tk()
            self.is_standalone = True
        else:
            self.root = tk.Toplevel(parent)
            self.is_standalone = False
        
        self.root.title("Klar Search Engine - Setup Wizard")
        self.root.geometry("800x600")
        
        # Initialize config manager
        self.config = ConfigManager()
        
        # Setup wizard state
        self.current_step = 0
        self.completed = False
        
        # Create UI
        self._create_ui()
        
        logger.info("Setup Wizard initialized")
    
    def _create_ui(self) -> None:
        """Create the wizard UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome to Klar Search Engine",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Content frame
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Show first step
        self._show_welcome_step()
        
        # Navigation buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.back_button = ttk.Button(
            button_frame,
            text="< Back",
            command=self._go_back,
            state=tk.DISABLED
        )
        self.back_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next >",
            command=self._go_next
        )
        self.next_button.pack(side=tk.RIGHT)
        
        self.finish_button = ttk.Button(
            button_frame,
            text="Finish",
            command=self._finish,
            state=tk.DISABLED
        )
        self.finish_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _show_welcome_step(self) -> None:
        """Show welcome step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        welcome_text = """
Welcome to Klar Search Engine Setup!

This wizard will help you configure Klar for first use.

Click 'Next' to continue with the setup process.
        """
        
        label = ttk.Label(
            self.content_frame,
            text=welcome_text,
            justify=tk.LEFT,
            font=("Arial", 11)
        )
        label.pack(pady=20)
    
    def _show_config_step(self) -> None:
        """Show configuration step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(
            self.content_frame,
            text="Configuration Settings",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 20))
        
        # Data path
        ttk.Label(self.content_frame, text="Data Directory:").pack(anchor=tk.W)
        self.data_path_var = tk.StringVar(value=self.config.get('data_path', 'data'))
        ttk.Entry(self.content_frame, textvariable=self.data_path_var, width=50).pack(pady=(0, 15))
        
        # Max workers
        ttk.Label(self.content_frame, text="Maximum Workers:").pack(anchor=tk.W)
        self.max_workers_var = tk.IntVar(value=self.config.get('max_workers', 2))
        ttk.Spinbox(self.content_frame, from_=1, to=8, textvariable=self.max_workers_var, width=10).pack(anchor=tk.W, pady=(0, 15))
        
        # Save settings
        ttk.Label(
            self.content_frame,
            text="These settings can be changed later in the configuration file.",
            font=("Arial", 9, "italic")
        ).pack(pady=20)
    
    def _show_complete_step(self) -> None:
        """Show completion step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        complete_text = """
Setup Complete!

Klar Search Engine is now configured and ready to use.

Click 'Finish' to close the wizard and start using Klar.
        """
        
        label = ttk.Label(
            self.content_frame,
            text=complete_text,
            justify=tk.LEFT,
            font=("Arial", 11)
        )
        label.pack(pady=20)
        
        # Enable finish button, disable next
        self.next_button.config(state=tk.DISABLED)
        self.finish_button.config(state=tk.NORMAL)
    
    def _go_next(self) -> None:
        """Go to next step"""
        if self.current_step == 0:
            # From welcome to config
            self.current_step = 1
            self._show_config_step()
            self.back_button.config(state=tk.NORMAL)
        elif self.current_step == 1:
            # From config to complete - save settings first
            self._save_settings()
            self.current_step = 2
            self._show_complete_step()
    
    def _go_back(self) -> None:
        """Go to previous step"""
        if self.current_step == 1:
            # From config to welcome
            self.current_step = 0
            self._show_welcome_step()
            self.back_button.config(state=tk.DISABLED)
        elif self.current_step == 2:
            # From complete to config
            self.current_step = 1
            self._show_config_step()
            self.next_button.config(state=tk.NORMAL)
            self.finish_button.config(state=tk.DISABLED)
    
    def _save_settings(self) -> None:
        """Save configuration settings"""
        try:
            if hasattr(self, 'data_path_var'):
                self.config.set('data_path', self.data_path_var.get())
            if hasattr(self, 'max_workers_var'):
                self.config.set('max_workers', self.max_workers_var.get())
            
            self.config.save_config()
            logger.info("Setup wizard settings saved")
        except Exception as e:
            logger.error(f"Error saving setup settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _finish(self) -> None:
        """Complete the wizard"""
        self.completed = True
        logger.info("Setup wizard completed")
        
        if self.is_standalone:
            self.root.quit()
        else:
            self.root.destroy()
    
    def run(self) -> bool:
        """
        Run the setup wizard
        
        Returns:
            True if setup was completed, False if cancelled
        """
        if self.is_standalone:
            self.root.mainloop()
        
        return self.completed


def main():
    """Main entry point for standalone execution"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    wizard = SetupWizard()
    completed = wizard.run()
    
    if completed:
        print("Setup completed successfully!")
    else:
        print("Setup was cancelled.")
    
    return 0 if completed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
