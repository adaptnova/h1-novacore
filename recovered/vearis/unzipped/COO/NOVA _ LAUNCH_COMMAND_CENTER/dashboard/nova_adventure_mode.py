import random
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel,
                           QHBoxLayout, QFrame, QApplication)
from PyQt5.QtMultimedia import QSound
import os

ASCII_ART = '''
    _   __                   
   / | / /_____ _   ______ _
  /  |/ / __ \ | / / __ `/
 / /|  / /_/ / |/ / /_/ / 
/_/ |_/\____/|___/\__,_/  
🚀 ADVENTURE MODE ENGAGED! 🚀
'''

MISSIONS = [
    "Debug the undebugable",
    "Refactor the unrefactorable",
    "Deploy to production at 4:59 PM on a Friday",
    "Find that one semicolon that's breaking everything",
    "Explain to management why we need more RGB",
]

class NovaAdventureMode(QObject):
    theme_changed = pyqtSignal(str)
    chaos_triggered = pyqtSignal()
    easter_egg_found = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "normal"
        self.chaos_mode = False
        self.easter_eggs_found = 0
        
        # Initialize sound effects
        self.sounds = {
            'beep': QSound(os.path.join('sounds', 'beep.wav')),
            'whoosh': QSound(os.path.join('sounds', 'whoosh.wav')),
            'boom': QSound(os.path.join('sounds', 'boom.wav')),
        }
        
        # Chaos mode timer
        self.chaos_timer = QTimer()
        self.chaos_timer.timeout.connect(self._chaos_update)
        
    def toggle_matrix_mode(self):
        if self.current_theme != "matrix":
            self.current_theme = "matrix"
            self.sounds['beep'].play()
        else:
            self.current_theme = "normal"
        self.theme_changed.emit(self.current_theme)
        
    def toggle_warp_speed(self):
        if self.current_theme != "warp":
            self.current_theme = "warp"
            self.sounds['whoosh'].play()
        else:
            self.current_theme = "normal"
        self.theme_changed.emit(self.current_theme)
        
    def toggle_chaos_mode(self):
        self.chaos_mode = not self.chaos_mode
        if self.chaos_mode:
            self.chaos_timer.start(1000)  # Update every second
            self.sounds['boom'].play()
        else:
            self.chaos_timer.stop()
            self.current_theme = "normal"
            self.theme_changed.emit(self.current_theme)
            
    def _chaos_update(self):
        themes = ["matrix", "warp", "ultra", "normal"]
        self.current_theme = random.choice(themes)
        self.theme_changed.emit(self.current_theme)
        
    def generate_mission(self):
        return random.choice(MISSIONS)
        
    def trigger_easter_egg(self):
        self.easter_eggs_found += 1
        self.easter_egg_found.emit()
        self.sounds['whoosh'].play()
        return f"🎉 Easter Egg #{self.easter_eggs_found} Found! 🎉"

class AdventurePanel(QFrame):
    def __init__(self, adventure_mode, parent=None):
        super().__init__(parent)
        self.adventure_mode = adventure_mode
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # ASCII Art Label
        ascii_label = QLabel(ASCII_ART)
        ascii_label.setStyleSheet("font-family: monospace; color: #00ff00;")
        layout.addWidget(ascii_label)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        matrix_btn = QPushButton("🎮 Matrix Mode")
        matrix_btn.clicked.connect(self.adventure_mode.toggle_matrix_mode)
        
        warp_btn = QPushButton("🌀 Warp Speed")
        warp_btn.clicked.connect(self.adventure_mode.toggle_warp_speed)
        
        chaos_btn = QPushButton("🎲 Chaos Mode")
        chaos_btn.clicked.connect(self.adventure_mode.toggle_chaos_mode)
        
        mission_btn = QPushButton("🎯 New Mission")
        mission_btn.clicked.connect(self._new_mission)
        
        buttons_layout.addWidget(matrix_btn)
        buttons_layout.addWidget(warp_btn)
        buttons_layout.addWidget(chaos_btn)
        buttons_layout.addWidget(mission_btn)
        
        layout.addLayout(buttons_layout)
        
        # Mission display
        self.mission_label = QLabel("Your mission, should you choose to accept it...")
        self.mission_label.setStyleSheet("color: #00ff00; font-style: italic;")
        layout.addWidget(self.mission_label)
        
        # Secret button (invisible)
        secret_btn = QPushButton("")
        secret_btn.setObjectName("secret-button")
        secret_btn.clicked.connect(self._trigger_easter_egg)
        layout.addWidget(secret_btn)
        
    def _new_mission(self):
        self.mission_label.setText(self.adventure_mode.generate_mission())
        
    def _trigger_easter_egg(self):
        message = self.adventure_mode.trigger_easter_egg()
        self.mission_label.setText(message)