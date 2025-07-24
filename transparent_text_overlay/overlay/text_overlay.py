
from __future__ import annotations
from PyQt5.QtWidgets import (
    QApplication,
    QTextEdit
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QTextBlockFormat, QTextCursor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from models import DisplaySettings

class DraggableTextEdit(QTextEdit):
    """Custom QTextEdit that allows dragging its parent when in edit mode."""
    def __init__(self, parent=None, text="No text", displaySettings: DisplaySettings = None):
        super().__init__(parent)
        self.overlay_widget = parent
        self.displaySettings = displaySettings
        self.dragging = False
        self.last_pos = QPoint()
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        self.setReadOnly(True)
        self.ttext = text
        QTextEdit.setText(self, text)
        QTextEdit.setFont(self, self.displaySettings.font)
        QTextEdit.setTextColor(self, self.displaySettings.color1)
        
        block_format = QTextBlockFormat()
        block_format.setLineHeight(100+self.displaySettings.lineSpace, QTextBlockFormat.ProportionalHeight)
        
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)

    def set_display_settings(self, sett: DisplaySettings):
        self.displaySettings = sett
        
    def updateFont(self):
        QTextEdit.setFont(self, self.displaySettings.font)
        QTextEdit.setTextColor(self, self.displaySettings.color1)

        print('ls:', self.displaySettings.lineSpace)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(100+self.displaySettings.lineSpace, QTextBlockFormat.ProportionalHeight)
        
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)
        self.viewport().update()
        
    def setTYext(self, text):
        self.ttext = text
        QTextEdit.setText(self, text)
        
        
    def mousePressEvent(self, event):
        if self.overlay_widget and self.overlay_widget.edit_mode:
            if event.button() == Qt.LeftButton:
                self.dragging = True
                self.last_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        
        if self.overlay_widget and self.overlay_widget.edit_mode and self.dragging:
            delta = event.globalPos() - self.last_pos
            self.overlay_widget.move(self.overlay_widget.pos() + delta)
            self.last_pos = event.globalPos()
            if self.overlay_widget.position_changed_callback:
                self.overlay_widget.position_changed_callback(self.overlay_widget.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            fs = self.displaySettings.font.pointSize()
            
            if delta > 0:
                fs += 1
            else:
                fs = max(1, fs - 1)

            self.displaySettings.font.setPointSize(fs)

            if self.overlay_widget is not None:
                self.overlay_widget.donwstream_fontsize_update(fs)
                
            QTextEdit.setFont(self, self.displaySettings.font)   
             
            self.viewport().update()
        else:
            super().wheelEvent(event)
       
