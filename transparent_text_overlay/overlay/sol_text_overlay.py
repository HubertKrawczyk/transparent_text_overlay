from PyQt5.QtWidgets import QApplication, QAbstractScrollArea, QScrollBar
from PyQt5.QtGui import QPainter, QColor, QFont, QTextLayout, QTextOption, QPainterPath, QPen
from PyQt5.QtCore import Qt, QPointF, QPoint
from PyQt5.QtGui import QTextCharFormat

from models import DisplaySettings

class OutlinedTextWidget(QAbstractScrollArea):
    def __init__(self, parent=None, text="No text", displaySettings: DisplaySettings = None):
        super().__init__()
        
        self.overlay_widget = parent
        self.displaySettings = displaySettings
        
        self.ttext = text

        self.last_pos = QPoint()
        self.viewport().setCursor(Qt.SizeAllCursor)

        self.layout_lines = []
        self.rebuild_layout()

        self.update_scrollbar()
        
    def set_display_settings(self, sett: DisplaySettings):
        self.displaySettings = sett
        
    def setTYext(self, text):
        self.ttext = text
        self.rebuild_layout()

    def updateFont(self):
        self.rebuild_layout()
        self.update_scrollbar()
        self.viewport().update()
        
    def rebuild_layout(self):
        """Prepares layout lines with QTextLayout"""
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.layout_lines.clear()

        max_line_width = 0

        y = 0
        
        for paragraph in self.ttext.splitlines():
            
            layout = QTextLayout(paragraph)
            layout.setTextOption(option)

            format = QTextCharFormat()
            format.setFont(self.displaySettings.font)

            format_range = QTextLayout.FormatRange()
            format_range.start = 0
            format_range.length = len(paragraph)
            format_range.format = format

            layout.setAdditionalFormats([format_range])
            layout.beginLayout()
            while True:
                line = layout.createLine()
                if not line.isValid():
                    break
                line.setLineWidth(float("inf")) 
                max_line_width = max(max_line_width, line.naturalTextWidth())
                line.setPosition(QPointF(0, y))
            
                y += line.height() + self.displaySettings.lineSpace
            layout.endLayout()
            self.layout_lines.append((layout, y)) 

        self.full_height = y
        self.full_width = int(max_line_width)
        self.horizontalScrollBar().setRange(0, int(max(0, max_line_width - self.viewport().width())))
        self.horizontalScrollBar().setPageStep(self.viewport().width())

    def update_scrollbar(self):
        scroll_range = max(0, int(self.full_height - self.viewport().height()))
        self.verticalScrollBar().setRange(0, scroll_range)
        self.verticalScrollBar().setPageStep(self.viewport().height())

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
                
            self.update()
            self.rebuild_layout()
            self.update_scrollbar()
            self.viewport().update()
        else:
            super().wheelEvent(event)
            
    def resizeEvent(self, event):
        self.rebuild_layout()
        self.update_scrollbar()
        self.viewport().update()
        
    def paintEvent(self, event):
        # print('re-paint',time.time())
        
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        y_offset = self.verticalScrollBar().value()
        painter.translate(0, -y_offset)

        x_offset = self.horizontalScrollBar().value()
        painter.translate(-x_offset, -y_offset)
        
        for layout, _ in self.layout_lines:
            for i in range(layout.lineCount()):

                line = layout.lineAt(i)
                text = layout.text()[line.textStart(): line.textStart() + line.textLength()]
                pos = line.position()


                ############################################ opt1
                
                
                x_cursor = pos.x() + self.displaySettings.outlineSize
                baseline_y = pos.y() + layout.lineAt(i).ascent()
                
                path = QPainterPath()
                path.addText(QPointF(x_cursor, baseline_y), self.displaySettings.font, text)

                painter.setPen(QPen(self.displaySettings.color2, self.displaySettings.outlineSize))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)

                painter.setPen(Qt.NoPen)
                painter.setBrush(self.displaySettings.color1)
                painter.drawPath(path)

                x_cursor += path.boundingRect().width()
                
                ############################################ opt2

                # # emoji and non-emoji
                # runs = []
                # current_run = ""
                # is_emoji_run = None

                # def is_emoji_char(c):
                #     return (0x1F600 <= ord(c) <= 0x1F64F or
                #             0x1F300 <= ord(c) <= 0x1F5FF or
                #             0x1F680 <= ord(c) <= 0x1F6FF or
                #             0x2600 <= ord(c) <= 0x26FF or
                #             0x2700 <= ord(c) <= 0x27BF)

                # for c in text:
                #     c_is_emoji = is_emoji_char(c)
                #     if is_emoji_run is None:
                #         is_emoji_run = c_is_emoji
                #         current_run = c
                #     elif c_is_emoji == is_emoji_run:
                #         current_run += c
                #     else:
                #         runs.append((current_run, is_emoji_run))
                #         current_run = c
                #         is_emoji_run = c_is_emoji
                # if current_run:
                #     runs.append((current_run, is_emoji_run))

                # x_cursor = pos.x()
                # baseline_y = pos.y() + layout.lineAt(i).ascent()

                # for run_text, run_is_emoji in runs:
                #     if run_is_emoji:
                #         emoji_font = QFont(self.displaySettings.font, self.displaySettings.font.pointSize())
                #         painter.setFont(emoji_font)
                #         painter.setPen(self.displaySettings.color2)
                #         painter.drawText(QPointF(x_cursor, baseline_y), run_text)

                #         width = painter.fontMetrics().width(run_text)
                #         x_cursor += width
                #     else:
                #         path = QPainterPath()
                #         path.addText(QPointF(x_cursor, baseline_y), self.displaySettings.font, run_text)

                #         painter.setPen(QPen(self.displaySettings.color2, self.displaySettings.outlineSize))
                #         painter.setBrush(Qt.NoBrush)
                #         painter.drawPath(path)

                #         painter.setPen(Qt.NoPen)
                #         painter.setBrush(self.displaySettings.color1)
                #         painter.drawPath(path)

                #         x_cursor += path.boundingRect().width()
                        
     
                
                
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
                
                
if __name__ == "__main__":
    app = QApplication([])

    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n" * 5
    )
    ds = DisplaySettings()
    ds.font = QFont("Times new roman", 50)
    ds.lineSpace = 6
    ds.color1 = QColor("red")
    ds.color2 = QColor("blue")
    ds.outlineSize = 3

    viewer = OutlinedTextWidget(None, text, ds)

    viewer.resize(600, 300)
    viewer.rebuild_layout()
    viewer.update_scrollbar()
    viewer.viewport().update()
    viewer.show()

    app.exec_()
