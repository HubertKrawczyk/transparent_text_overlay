from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from PyQt5.QtGui import QFont, QColor
from enum import Enum


@dataclass
class DisplaySettings:
    font: QFont = None
    color1: QColor = None
    color2: QColor = None
    lineSpace: int = None
    widgetType: Literal[0, 1] = None
    x: int = None
    y: int = None
    w: int = None
    h: int = None
    outlineSize: int = None
    textFilePath: str = None
    
    
class ConfigProps(Enum):
    TEXT = "text"
    X = "x"
    Y = "y"
    W = "w"
    H = "h"
    FONT_NAME = "font_name"
    FONT_SIZE = "font_size"
    COLOR1 = "color1"
    COLOR2 = "color2"
    TEXT_FILE_PATH = "text_file_path"
    WATCH_FILE = "watch_file"
    LINE_SPACE = "line_space"
    TEXT_OVERLAY_TYPE = "text_overlay_type"
    DRAGGABLE = "draggable"
    OUTLINE_SIZE = "outline_size"
    WATCH_FILE_SAVEBACK = "watch_file_saveback"