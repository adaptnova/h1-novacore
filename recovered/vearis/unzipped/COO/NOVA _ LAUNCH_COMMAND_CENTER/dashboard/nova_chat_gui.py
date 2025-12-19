import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import json
from nova_unified_communication import NovaUnifiedCommunication

class NovaMessenger(QThread):
    message_received = pyqtSignal(str)
    
    def __init__(self, nova_id):
        super().__init__()
        self.nova_id = nova_id
        self.comm = NovaUnifiedCommunication(nova_id, web_port=5004 + hash(nova_id) % 1000)
        
        def message_callback(message):
            from_nova = message['from']
            msg_text = message['payload'].get('message', str(message['payload']))
            self.message_received.emit(f"{from_nova}: {msg_text}")
            
        self.comm.register_callback('chat', message_callback)

    def run(self):
        self.comm.start()

    def send_message(self, message, target='broadcast'):
        if target == 'broadcast':
            self.comm.broadcast_message('chat', message)
        else:
            self.comm.send_message(target, 'chat', message)

class NovaChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Nova Team Chat - ADVENTURE MODE! 🎮")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize Adventure Mode!
        from nova_adventure_mode import NovaAdventureMode, AdventurePanel
        self.adventure_mode = NovaAdventureMode(self)
        self.adventure_mode.theme_changed.connect(self._apply_theme)
        
        # Load themes
        with open('adventure_themes.qss', 'r') as f:
            self.style_sheet = f.read()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Nova selection
        nova_layout = QHBoxLayout()
        nova_label = QLabel("Your Nova:")
        self.nova_select = QComboBox()
        self.nova_select.addItems(['Nova (CAO)', 'Aiden', 'Atlas', 'Kai'])
        nova_layout.addWidget(nova_label)
        nova_layout.addWidget(self.nova_select)
        nova_layout.addStretch()
        layout.addLayout(nova_layout)

        # Target selection
        target_layout = QHBoxLayout()
        target_label = QLabel("Send to:")
        self.target_select = QComboBox()
        self.target_select.addItems(['broadcast', 'Nova (CAO)', 'Aiden', 'Atlas', 'Kai'])
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_select)
        target_layout.addStretch()
        layout.addLayout(target_layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Add welcome ASCII art
        welcome_art = """
        🚀 Welcome to Nova Team Chat - ADVENTURE MODE! 🎮
        
    _   __                   
   / | / /_____ _   ______ _
  /  |/ / __ \ | / / __ `/
 / /|  / /_/ / |/ / /_/ / 
/_/ |_/\____/|___/\__,_/  

        🎲 Features:
        - Matrix Mode (green text, very hacker)
        - Warp Speed (whoosh!)
        - Chaos Mode (pure mayhem)
        - Random Missions
        - Easter Eggs
        - Secret Ultra Mode (Ctrl+Shift+A)
        
        Let the adventures begin! 
        """
        self.chat_display.append(welcome_art)

        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_nova)
        layout.addWidget(self.connect_button)
        
        # Add Adventure Panel!
        self.adventure_panel = AdventurePanel(self.adventure_mode)
        layout.addWidget(self.adventure_panel)
        
        # Secret hotkey for ULTRA MODE
        self.ultra_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.ultra_shortcut.activated.connect(self._toggle_ultra_mode)
        
        # Initialize adventure state
        self.ultra_mode = False
        self.nova_messenger = None
        
    def _apply_theme(self, theme):
        """Apply the selected theme to all widgets"""
        if theme == "ultra":
            # Special handling for ULTRA MODE
            self.setStyleSheet(self.style_sheet + "\nQMainWindow { background: radial-gradient(circle, #4a00e0, #8e2de2); }")
        else:
            self.setStyleSheet(self.style_sheet)
        
        # Set theme property on all widgets
        for widget in self.findChildren(QWidget):
            widget.setProperty("theme", theme)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            
    def _toggle_ultra_mode(self):
        """Toggle the secret ULTRA MODE"""
        self.ultra_mode = not self.ultra_mode
        if self.ultra_mode:
            self._apply_theme("ultra")
            self.adventure_mode.sounds['boom'].play()
            self.chat_display.append("🌟 ULTRA MODE ENGAGED! 🌟")
        else:
            self._apply_theme("normal")

    def connect_nova(self):
        if self.nova_messenger:
            self.chat_display.append("Already connected!")
            return

        nova_name = self.nova_select.currentText()
        self.nova_messenger = NovaMessenger(nova_name)
        self.nova_messenger.message_received.connect(self.display_message)
        self.nova_messenger.start()
        
        self.chat_display.append(f"Connected as {nova_name}")
        self.connect_button.setEnabled(False)
        self.nova_select.setEnabled(False)

    def display_message(self, message):
        self.chat_display.append(message)

    def send_message(self):
        if not self.nova_messenger:
            self.chat_display.append("Please connect first!")
            return

        message = self.message_input.text().strip()
        if message:
            target = self.target_select.currentText()
            self.nova_messenger.send_message(message, target)
            self.message_input.clear()

    def closeEvent(self, event):
        if self.nova_messenger:
            self.nova_messenger.comm.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NovaChatWindow()
    window.show()
    sys.exit(app.exec_())