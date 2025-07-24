from __future__ import annotations
import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QSpinBox,
    QTextEdit, QSizeGrip, QColorDialog, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon
from models import ConfigProps, DisplaySettings
from overlay.sol_text_overlay import OutlinedTextWidget
from overlay.text_overlay import DraggableTextEdit
from file_watcher import FileWatcher

CONFIG_FILE = "transparent_text_overlay_config.json"
DEFAULT_TEXT_FILE_PATH = "text.txt"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return json.loads("{}F")
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
        
def load_text(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "No text loaded, use the settings window or put text to '"+path+"'"

def save_text(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

class SettingsWindow(QWidget):
    def __init__(self, overlay: OverlayWidget, config, displaySettings: DisplaySettings):
        super().__init__()
        self.overlay = overlay
        if not overlay:
            raise "No overlay provided"
        
        overlay.register_settings(self)
        
        self.displaySettings = displaySettings

        self.setWindowTitle("Overlay Settings")
        self.config = config
        
        self.text_input = QTextEdit()
        self.saved_text = load_text(self.displaySettings.textFilePath)
        self.text_input.setPlainText(self.saved_text) 
        self.text_input.setMinimumHeight(80) 
          
        self.overlay.setText(self.saved_text) 
        
        self.x_input = QSpinBox()
        self.x_input.setRange(0, 3000)
        self.x_input.setPrefix("X: ")
        self.x_input.setValue(self.displaySettings.x)

            
        self.y_input = QSpinBox()
        self.y_input.setRange(0, 3000)
        self.y_input.setPrefix("Y: ")
        self.y_input.setValue(self.displaySettings.y)
        
        self.text_type_combobox = QComboBox()
        self.text_type_combobox.addItem('Simple')
        self.text_type_combobox.addItem("Outlined text (slow)")
        self.text_type_combobox.setCurrentIndex(self.displaySettings.widgetType)
        self.selected_text_type = self.displaySettings.widgetType

        self.outline_size_input = QSpinBox()
        self.outline_size_input.setRange(0, 50)
        self.outline_size_input.setPrefix("Outline size: ")
        self.outline_size_input.setValue(self.displaySettings.outlineSize)
        
        self.font_name_input = QLineEdit()
        self.font_name_input.setText(self.displaySettings.font.family())
        
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(0, 300)
        self.font_size_input.setPrefix("Font Size: ")
        self.font_size_input.setValue(self.displaySettings.font.pointSize())
        
        self.line_space_input = QSpinBox()
        self.line_space_input.setRange(-50, 300)
        self.line_space_input.setPrefix("Linespace: ")
        self.line_space_input.setValue(self.displaySettings.lineSpace)
        
        self.color_button1 = QPushButton("Pick Color1", self)
        self.color_button1.clicked.connect(self.open_color_picker1)
        self.color_button1.resize(150, 40)
        self.color_button1.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {self.displaySettings.color1.name()};
                border-radius: 4px;
            }}
        """)
        
        self.color_button2 = QPushButton("Pick Color2", self)
        self.color_button2.clicked.connect(self.open_color_picker2)
        self.color_button2.resize(150, 40)
        self.color_button2.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {self.displaySettings.color2.name()};
                border-radius: 4px;
            }}
        """)

        
        self.drag_checkbox = QCheckBox("Draggable (transparent switch)")
        self.drag_checkbox.setChecked(config.get(ConfigProps.DRAGGABLE.value, True)) 
        self.drag_checkbox.stateChanged.connect(self.drag_changed)
        
        self.show_overlay_checkbox = QCheckBox("Show overlay")
        self.show_overlay_checkbox.setChecked(True) 
        self.show_overlay_checkbox.stateChanged.connect(self.show_overlay_changed)
        
        self.apply_button = QPushButton("Apply and save above settings")
        self.exit_button = QPushButton("Exit")

        self.filewatch_checkbox = QCheckBox("Current watch file")
        self.filewatch_checkbox.setChecked(config.get(ConfigProps.WATCH_FILE.value, False)) 
        self.filewatch_checkbox.stateChanged.connect(self.filewatch_checkbox_changed)
        
        self.filewatch_input = QLineEdit()
        self.filewatch_input.setText(config.get(ConfigProps.TEXT_FILE_PATH.value, "text.txt"))
        
        self.filewatch_apply_button = QPushButton("Change path", self)
        self.filewatch_apply_button.clicked.connect(self.filewatch_apply_button_func)
        
        self.filewatch_saveback_checkbox = QCheckBox("Save back to file")
        self.filewatch_saveback_checkbox.setChecked(config.get(ConfigProps.WATCH_FILE_SAVEBACK.value, False)) 

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.text_input)
        
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(self.x_input)
        coord_layout.addWidget(self.y_input)
        coord_layout.addWidget(self.text_type_combobox)
        coord_layout.addWidget(self.outline_size_input)
        layout.addLayout(coord_layout)

        font_layout = QHBoxLayout()
        font_layout.addWidget(self.font_name_input)
        font_layout.addWidget(self.font_size_input)
        font_layout.addWidget(self.line_space_input)
        layout.addLayout(font_layout)
        
        font_layout.addWidget(self.color_button1)
        font_layout.addWidget(self.color_button2)
        
        layout.addWidget(self.apply_button)
        
        drag_layout = QHBoxLayout()
        drag_layout.addWidget(self.drag_checkbox)
        
        self.drag_arrow = QLabel("<----- Move/resize overlay")
        self.drag_checkbox.setContentsMargins(0, 0, 0, 0)
        self.drag_arrow.setContentsMargins(0, 0, 0, 0)
        drag_layout.addWidget(self.drag_arrow)
        layout.addLayout(drag_layout)
        
        layout.addWidget(self.show_overlay_checkbox)
        
        layout.addWidget(self.exit_button)

        filewatch_layout = QHBoxLayout()
        filewatch_layout.addWidget(self.filewatch_checkbox)
        filewatch_layout.addWidget(self.filewatch_input)
        filewatch_layout.addWidget(self.filewatch_apply_button)
        filewatch_layout.addWidget(self.filewatch_saveback_checkbox)
        layout.addLayout(filewatch_layout)
        self.setMinimumWidth(300)
 
        self.setLayout(layout)
        
        self.apply_button.clicked.connect(self.apply_settings)
        self.exit_button.clicked.connect(self.exit_all)
        
        self.overlay.set_position_changed_callback(self.update_coords_from_overlay)
        self.move(50, 50)

        self.show()
        self.watcher = FileWatcher("./"+DEFAULT_TEXT_FILE_PATH, self.on_file_updated, self.saved_text)
        
        if self.filewatch_checkbox.isChecked() and config.get(ConfigProps.TEXT_FILE_PATH.value, False) and self.filewatch_input.text():
            self.watcher.start(self.filewatch_input.text())

    def open_color_picker1(self):
        color = QColorDialog.getColor(self.displaySettings.color1, self, "Select Color")
        if color.isValid():
            self.displaySettings.color1 = color
            self.color_button1.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {self.displaySettings.color1.name()};
                    border-radius: 4px;
                }}
            """)
    
    def open_color_picker2(self):
        color = QColorDialog.getColor(self.displaySettings.color2, self, "Select Color")
        if color.isValid():
            self.displaySettings.color2 = color
            self.color_button2.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {self.displaySettings.color2.name()};
                    border-radius: 4px;
                }}
            """)
                    
    def on_file_updated(self, new_text):
        print("File changed!")
        if new_text and new_text != self.saved_text:
            print('setting text')
            self.saved_text = new_text
            self.text_input.setPlainText(self.saved_text) 
            self.overlay.setText(self.saved_text) 
                 
    def filewatch_checkbox_changed(self, state):
        if state == 2:
            self.watcher.start(self.filewatch_input.text())
        else:
            self.watcher.stop()
            
    def filewatch_apply_button_func(self):
        self.watcher.stop()
        self.watcher.start(self.filewatch_input.text())

    def show_overlay_changed(self, state):
        if state == 2 and  not self.overlay.isVisible():
            self.overlay.show()
        else:
            self.overlay.hide()
            
    def drag_changed(self, state):
        if state == 2:
            self.overlay.enter_edit_mode(True)
        else:
            self.overlay.enter_edit_mode(False)

    def update_coords_from_overlay(self, pos):
        self.x_input.blockSignals(True)
        self.y_input.blockSignals(True)
        self.x_input.setValue(pos.x())
        self.y_input.setValue(pos.y())
        self.x_input.blockSignals(False)
        self.y_input.blockSignals(False)
   
    def donwstream_fontsize_update(self, fontsize):
        self.font_size_input.setValue(fontsize)
         
    def apply_settings(self):
        if self.text_type_combobox.currentIndex() != self.displaySettings.widgetType:
            self.displaySettings.widgetType = self.text_type_combobox.currentIndex() if self.text_type_combobox.currentIndex() in [0,1] else 0
            self.overlay.change_widget_type(self.displaySettings.widgetType)

        new_text = self.text_input.toPlainText()
        if new_text is None:
            new_text = ""
        
        if new_text != self.saved_text:
            print('setting new text')
            self.overlay.setText(new_text)
            self.saved_text = new_text
            
            if self.filewatch_saveback_checkbox.isChecked():
                print('saving new text to file '+self.displaySettings.textFilePath)
                self.watcher.pause()
                save_text(new_text, self.displaySettings.textFilePath)
                QTimer.singleShot(2000, self.watcher.resume)
                
            # save_text(new_text, self.displaySettings.textFilePath)

        font_name = self.font_name_input.text()
        font_size = self.font_size_input.value()
        line_space = self.line_space_input.value()
        self.displaySettings.font = QFont(font_name, font_size)
        self.displaySettings.lineSpace = line_space
        
        self.displaySettings.outlineSize = self.outline_size_input.value()

        self.displaySettings.x = self.x_input.value()
        self.displaySettings.y = self.y_input.value()
        self.overlay.move(self.displaySettings.x, self.displaySettings.y)

        self.overlay.updateFontR()
        draggable = self.drag_checkbox.isChecked()

        self.config.update({
            # ConfigProps.TEXT.value: new_text,
            ConfigProps.X.value: self.displaySettings.x,
            ConfigProps.Y.value: self.displaySettings.y,
            ConfigProps.W.value: self.displaySettings.w,
            ConfigProps.H.value: self.displaySettings.h,
            ConfigProps.DRAGGABLE.value: draggable,
            "settings_x": self.pos().x(),
            "settings_y": self.pos().y(),
            ConfigProps.FONT_NAME.value: font_name,
            ConfigProps.FONT_SIZE.value: font_size,
            ConfigProps.COLOR1.value: self.displaySettings.color1.name(),
            ConfigProps.COLOR2.value: self.displaySettings.color2.name(),
            ConfigProps.LINE_SPACE.value: line_space,
            ConfigProps.TEXT_FILE_PATH.value: self.filewatch_input.text(),
            ConfigProps.WATCH_FILE.value: self.filewatch_checkbox.isChecked(),
            ConfigProps.TEXT_OVERLAY_TYPE.value: self.displaySettings.widgetType,
            ConfigProps.OUTLINE_SIZE.value: self.displaySettings.outlineSize,
            ConfigProps.WATCH_FILE_SAVEBACK.value: self.filewatch_saveback_checkbox.isChecked(),
        })
        save_config(self.config)

    def exit_all(self):
        self.overlay.close()
        self.close()


class OverlayWidget(QWidget):
    def __init__(self, config, displaySettings: DisplaySettings):
        super().__init__()
        self.displaySettings = displaySettings
        self.settings = None
        self.edit_mode = config.get(ConfigProps.DRAGGABLE.value, True)

        self.text_widget_type = self.displaySettings.widgetType
        self.text_font = self.displaySettings.font
        
        print('twt', self.text_widget_type)
        if self.text_widget_type == 0:
            self.text_edit = DraggableTextEdit(self, "No text", self.displaySettings)
        elif self.text_widget_type == 1:
            self.text_edit = OutlinedTextWidget(self, "No text", self.displaySettings)
        else:
            self.text_edit = DraggableTextEdit(self, "No text", self.displaySettings)
            
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        self.size_grip = QSizeGrip(self)

        self.mylayout = QVBoxLayout()
        self.mylayout.setContentsMargins(10, 10, 10, 10)
        self.mylayout.addWidget(self.text_edit)
        self.mylayout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        self.setLayout(self.mylayout)
        
        if self.edit_mode:
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
            self.setStyleSheet("background-color: rgba(40, 40, 40, 200); border: 2px solid red;")
            self.text_edit.setStyleSheet("background-color: rgba(0, 0, 0, 50); border: 2px dashed red")
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
            self.setStyleSheet("background-color: transparent;")
            self.text_edit.setStyleSheet("background-color: transparent; border: none;")
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
        self.text_edit.setEnabled(self.edit_mode) 

        if self.displaySettings.w is not None and self.displaySettings.h is not None:
            self.resize(displaySettings.w, displaySettings.h)
        if self.displaySettings.x is not None and self.displaySettings.y is not None:
            self.move(displaySettings.x, displaySettings.y)

        self.position_changed_callback = None
        self.show()
            
    def register_settings(self, sett: SettingsWindow):
        self.settings = sett
     
    def set_display_settingsR(self, sett: DisplaySettings):
        self.displaySettings = sett
        self.text_edit.set_display_settings(sett)
           
    def change_widget_type(self, new_val):
        if new_val == self.text_widget_type:
            return
        print(f'changing from {self.text_widget_type} to {new_val}')
        self.text_widget_type = new_val
        
        self.mylayout.removeWidget(self.text_edit)
        self.text_edit.deleteLater()
        
        new_widget = OutlinedTextWidget(self, self.text, self.displaySettings) if self.text_widget_type == 1 else DraggableTextEdit(self, self.text, self.displaySettings)
        self.mylayout.insertWidget(0, new_widget)
        self.text_edit = new_widget
        
        self.setText(self.text)        
        
    def donwstream_fontsize_update(self, fontsize):
        self.settings.donwstream_fontsize_update(fontsize)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_size = self.size()
        
        self.displaySettings.w = new_size.width()
        self.displaySettings.h = new_size.height()
        
            
    def set_position_changed_callback(self, callback):
        self.position_changed_callback = callback

    def enter_edit_mode(self, enabled: bool):
        # scroll_pos = self.text_edit.verticalScrollBar().value()
        self.edit_mode = enabled
        geometry = self.geometry()
        self.hide()
        
        if enabled:
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
        self.setGeometry(geometry)
        self.show()
        print('edit mode', enabled)
        
        self.text_edit.setEnabled(enabled)
  
        if enabled:
            self.setStyleSheet("background-color: rgba(40, 40, 40, 200); border: 2px solid red;")
            self.text_edit.setStyleSheet("background-color: rgba(0, 0, 0, 50); border: 2px dashed red")
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setStyleSheet("background-color: transparent;")
            self.text_edit.setStyleSheet("background-color: transparent; border: none; margin: 2px")
            self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.adjustSize()

        self.setGeometry(geometry)

    def updateFontR(self):
        self.text_edit.updateFont()
    
    def setText(self, content):
        self.text = content
        self.text_edit.setTYext(content)
        self.text_edit.updateFont()

def initDisplaySettings(config):
    displaySettings = DisplaySettings()
    displaySettings.color1 = QColor(config.get(ConfigProps.COLOR1.value, "white"))
    displaySettings.color2 = QColor(config.get(ConfigProps.COLOR2.value, "black"))
    displaySettings.font = QFont(config.get(ConfigProps.FONT_NAME.value, "Arial"), config.get(ConfigProps.FONT_SIZE.value, 16))
    displaySettings.lineSpace = config.get(ConfigProps.LINE_SPACE.value, 5)
    displaySettings.x = config.get(ConfigProps.X.value, 100)
    displaySettings.y = config.get(ConfigProps.Y.value, 100)
    displaySettings.w = config.get(ConfigProps.W.value, 200)
    displaySettings.h = config.get(ConfigProps.H.value, 600)
    displaySettings.widgetType = config.get(ConfigProps.TEXT_OVERLAY_TYPE.value, 0)
    displaySettings.outlineSize = config.get(ConfigProps.OUTLINE_SIZE.value, 2)
    displaySettings.textFilePath = config.get(ConfigProps.TEXT_FILE_PATH.value, DEFAULT_TEXT_FILE_PATH)
    return displaySettings

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller extracts to this temp dir
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = resource_path("icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    config = load_config()
    
    ds = initDisplaySettings(config)
    
    overlay_window = OverlayWidget(config, ds)
    settings_window = SettingsWindow(overlay_window, config, ds)
    sys.exit(app.exec_())
