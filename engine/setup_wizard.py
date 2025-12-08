"""
Klar Setup Wizard
First-run configuration for local search mode and data directory
"""

import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QPushButton, QLineEdit, QFileDialog, QCheckBox, QWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon


class SetupWizard(QDialog):
    """
    First-run setup wizard for Klar browser.
    Configures offline search and data directory preferences.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Klar Setup Wizard')
        self.setGeometry(100, 100, 600, 500)
        self.config = {}
        self.current_step = 0
        self.setup_ui()
        self.show_step(0)
    
    def setup_ui(self):
        """Setup the wizard interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel('Klar Setup Wizard')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel('Configure your Klar browser experience')
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet('color: #666;')
        layout.addWidget(subtitle)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.content_widget)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        layout.addWidget(self.progress)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.prev_btn = QPushButton('< Previous')
        self.prev_btn.clicked.connect(self.previous_step)
        button_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton('Next >')
        self.next_btn.clicked.connect(self.next_step)
        button_layout.addWidget(self.next_btn)
        
        self.finish_btn = QPushButton('Finish')
        self.finish_btn.clicked.connect(self.finish)
        self.finish_btn.hide()
        button_layout.addWidget(self.finish_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def show_step(self, step: int):
        """Display a specific setup step"""
        self.current_step = step
        self.update_progress()
        
        # Clear content layout
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget().deleteLater()
        
        if step == 0:
            self.show_welcome()
        elif step == 1:
            self.show_offline_mode()
        elif step == 2:
            self.show_data_location()
        elif step == 3:
            self.show_completion()
        
        # Update buttons
        self.prev_btn.setEnabled(step > 0)
        self.prev_btn.setVisible(step < 3)
        self.next_btn.setVisible(step < 2)
        self.finish_btn.setVisible(step >= 2)
    
    def show_welcome(self):
        """Welcome step"""
        label = QLabel(
            'Welcome to Klar 3.0 - The Swedish Browser\n\n'
            'This setup wizard will help you configure:\n'
            '• Offline search mode (LOKI)\n'
            '• Custom data directory for cached pages\n\n'
            'You can skip these settings and use online mode only.'
        )
        label.setWordWrap(True)
        label.setStyleSheet('line-height: 1.6; font-size: 12px;')
        self.content_layout.addWidget(label)
        self.content_layout.addStretch()
    
    def show_offline_mode(self):
        """Offline mode configuration step"""
        label = QLabel('Enable Local Search (LOKI)?')
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        self.content_layout.addWidget(label)
        
        info = QLabel(
            'LOKI allows you to search previously visited websites even without internet.\n\n'
            'When enabled:\n'
            '• Pages you visit are cached locally\n'
            '• Search works offline on cached content\n'
            '• No additional cost (uses local storage)\n\n'
            'When disabled:\n'
            '• Only online search is available\n'
            '• Requires internet connection\n'
            '• No local caching'
        )
        info.setWordWrap(True)
        info.setStyleSheet('color: #666; font-size: 11px;')
        self.content_layout.addWidget(info)
        
        self.content_layout.addSpacing(20)
        
        self.offline_group = QButtonGroup()
        self.offline_yes = QRadioButton('Yes, enable local search')
        self.offline_yes.setChecked(True)
        self.offline_no = QRadioButton('No, online mode only')
        
        self.offline_group.addButton(self.offline_yes)
        self.offline_group.addButton(self.offline_no)
        
        self.content_layout.addWidget(self.offline_yes)
        self.content_layout.addWidget(self.offline_no)
        self.content_layout.addStretch()
        
        self.config['offline_mode'] = True
        self.offline_yes.toggled.connect(lambda checked: self.config.update({'offline_mode': checked}))
    
    def show_data_location(self):
        """Data directory configuration step"""
        label = QLabel('Select Data Directory')
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        self.content_layout.addWidget(label)
        
        info = QLabel(
            'Choose where Klar stores cached pages and search index:\n\n'
            'Default: ~/.klar/klar_data/\n'
            'This folder will contain:\n'
            '• Cached website pages (LOKI database)\n'
            '• Search index\n'
            '• Browsing history\n\n'
            f'Current: {self.get_default_data_path()}'
        )
        info.setWordWrap(True)
        info.setStyleSheet('color: #666; font-size: 11px;')
        self.content_layout.addWidget(info)
        
        self.content_layout.addSpacing(15)
        
        # Default location option
        self.default_location = QRadioButton(f'Use default ({self.get_default_data_path()})')
        self.default_location.setChecked(True)
        self.content_layout.addWidget(self.default_location)
        
        # Custom location option
        custom_layout = QHBoxLayout()
        self.custom_location = QRadioButton('Custom location:')
        custom_layout.addWidget(self.custom_location)
        
        self.path_input = QLineEdit()
        self.path_input.setEnabled(False)
        self.path_input.setText(self.get_default_data_path())
        custom_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton('Browse...')
        browse_btn.clicked.connect(self.browse_directory)
        custom_layout.addWidget(browse_btn)
        
        self.content_layout.addLayout(custom_layout)
        
        self.default_location.toggled.connect(lambda checked: self.path_input.setEnabled(not checked))
        self.custom_location.toggled.connect(lambda checked: self.path_input.setEnabled(checked))
        
        self.content_layout.addStretch()
        
        # Store selection
        def update_path():
            if self.default_location.isChecked():
                self.config['data_path'] = self.get_default_data_path()
            else:
                self.config['data_path'] = self.path_input.text()
        
        self.default_location.toggled.connect(update_path)
        self.custom_location.toggled.connect(update_path)
        update_path()
    
    def show_completion(self):
        """Completion summary step"""
        label = QLabel('Setup Complete!')
        label_font = QFont()
        label_font.setPointSize(14)
        label_font.setBold(True)
        label.setFont(label_font)
        self.content_layout.addWidget(label)
        
        summary = QLabel(
            f'Your Klar configuration:\n\n'
            f'Offline Search (LOKI): '
            f'{"Enabled" if self.config.get("offline_mode") else "Disabled"}\n\n'
            f'Data Directory: {self.config.get("data_path", self.get_default_data_path())}\n\n\n'
            f'You can change these settings anytime in Preferences.'
        )
        summary.setWordWrap(True)
        summary.setStyleSheet('font-size: 12px; line-height: 1.8;')
        self.content_layout.addWidget(summary)
        self.content_layout.addStretch()
    
    def browse_directory(self):
        """Browse for custom data directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            'Select Data Directory',
            self.get_default_data_path()
        )
        if directory:
            self.path_input.setText(directory)
            self.config['data_path'] = directory
    
    def update_progress(self):
        """Update progress bar"""
        progress = int((self.current_step / 3) * 100)
        self.progress.setValue(progress)
    
    def previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def next_step(self):
        """Go to next step"""
        if self.current_step < 3:
            self.show_step(self.current_step + 1)
    
    def finish(self):
        """Complete setup and save configuration"""
        self.save_config()
        self.accept()
    
    def save_config(self):
        """Save setup configuration to file"""
        config_path = Path.home() / '.klar' / 'config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data_path = Path(self.config.get('data_path', self.get_default_data_path()))
        data_path.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'offline_mode': self.config.get('offline_mode', True),
            'data_path': str(self.config.get('data_path', self.get_default_data_path())),
            'setup_complete': True,
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f'[Setup] Configuration saved to {config_path}')
        print(f'[Setup] Offline mode: {config_data["offline_mode"]}')
        print(f'[Setup] Data directory: {config_data["data_path"]}')
    
    @staticmethod
    def get_default_data_path() -> str:
        """Get default data directory path"""
        return str(Path.home() / '.klar' / 'klar_data')
    
    @staticmethod
    def is_setup_complete() -> bool:
        """Check if setup has been completed"""
        config_path = Path.home() / '.klar' / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('setup_complete', False)
            except:
                return False
        return False
    
    @staticmethod
    def load_config() -> dict:
        """Load saved configuration"""
        config_path = Path.home() / '.klar' / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'offline_mode': True,
            'data_path': SetupWizard.get_default_data_path(),
            'setup_complete': False,
        }
