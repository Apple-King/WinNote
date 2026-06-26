# =================================================================
# WinNote - Windows笔记应用
# 基于PyQt6开发的macOS Notes风格笔记客户端
# =================================================================

import sys
import os
import json
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextEdit,
    QLineEdit, QLabel, QStyleFactory, QPushButton, QSizePolicy, QFrame
)
from PyQt6.QtGui import QTextCharFormat, QAction, QFont, QTextDocument, QIcon, QPixmap, QImage, QDrag, QTextCursor, QKeySequence
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QBuffer, QIODevice
from PIL import Image, ImageDraw

# =================================================================
# 常量定义
# =================================================================

# 样式常量
COLORS = {
    'primary': '#1c1c1e',       # 主文字
    'secondary': '#8e8e93',      # 次要文字
    'tertiary': '#aeaeb2',       # 辅助文字
    'background': '#f2f2f7',      # 背景色
    'hover': '#d1d1d6',          # 悬停效果
    'selected': '#c7c7cc',       # 选中效果
    'separator': '#d1d1d6',     # 分隔线
    'accent': '#3a3a3c',         # 强调色
}

FONTS = {
    'title': ('Times New Roman, 楷体', 14, QFont.Weight.DemiBold),
    'preview': ('Times New Roman, 楷体', 11, QFont.Weight.Normal),
    'date': ('Times New Roman, 楷体', 11, QFont.Weight.Normal),
    'editor': ('Times New Roman, 楷体', 15, QFont.Weight.Normal),
    'editor_title': ('Times New Roman, 楷体', 28, QFont.Weight.Bold),
    'toolbar': ('Arial', 16, QFont.Weight.Bold),
}

# 布局常量
SIDEBAR_WIDTH = 300
TOOLBAR_HEIGHT = 44
BUTTON_SIZE = 36
PREVIEW_MAX_LENGTH = 8

# 字体大小设置
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 32
DEFAULT_FONT_SIZE = 15

# 软件版本
VERSION = "1.0.1"

# =================================================================
# 翻译系统
# =================================================================

# 语言定义
LANGUAGES = {
    'en': 'English',
    'zh': '中文'
}

# 翻译字典
TRANSLATIONS = {
    'en': {
        # 菜单
        'menu_file': 'File',
        'menu_new_note': 'New Note',
        'menu_delete': 'Delete',
        'menu_language': 'Language',
        'menu_help': 'Help',
        'menu_about': 'About WinNote',
        
        # 占位符
        'placeholder_title': 'Title',
        'placeholder_search': 'Search',
        'placeholder_editor': 'Start typing...',
        
        # 其他
        'untitled': 'Untitled',
        'about_title': 'About WinNote',
        'about_description': 'A macOS Notes-style note-taking application for Windows.',
        'about_version': 'Version',
        'about_author': 'Developed with PyQt6',
        
        # 工具栏提示
        'tooltip_bold': 'Bold (Ctrl+B)',
        'tooltip_italic': 'Italic (Ctrl+I)',
        'tooltip_strikethrough': 'Strikethrough (Ctrl+S)',
        # 'tooltip_font_increase': 'Increase font size',
        # 'tooltip_font_decrease': 'Decrease font size',
        'placeholder_note_search': 'Search in note...',
    },
    'zh': {
        # 菜单
        'menu_file': '文件',
        'menu_new_note': '新建笔记',
        'menu_delete': '删除',
        'menu_language': '语言',
        'menu_help': '帮助',
        'menu_about': '关于 WinNote',
        
        # 占位符
        'placeholder_title': '标题',
        'placeholder_search': '搜索',
        'placeholder_editor': '开始输入...',
        
        # 其他
        'untitled': '无标题',
        'about_title': '关于 WinNote',
        'about_description': '一个基于 macOS Notes 风格的 Windows 笔记应用。',
        'about_version': '版本',
        'about_author': '使用 PyQt6 开发',
        
        # 工具栏提示
        'tooltip_bold': '加粗 (Ctrl+B)',
        'tooltip_italic': '斜体 (Ctrl+I)',
        'tooltip_strikethrough': '删除线 (Ctrl+S)',
        # 'tooltip_font_increase': '增大字体',
        # 'tooltip_font_decrease': '减小字体',
        'placeholder_note_search': '在笔记中搜索...',
    }
}

# 当前语言
current_language = 'en'

def tr(key):
    """翻译函数"""
    return TRANSLATIONS.get(current_language, TRANSLATIONS['en']).get(key, key)

def set_language(lang):
    """设置语言"""
    global current_language
    current_language = lang

# =================================================================
# 样式表定义
# =================================================================

STYLES = {
    'main': """
        QMainWindow {
            background-color: #f5f5f5;
        }
    """,
    'sidebar': """
        QWidget {
            background-color: #f0f0f0;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }
    """,
    'search_container': "background-color: #f2f2f7; padding: 10px; border-top-left-radius: 10px;",
    'search_box': """
        QLineEdit {
            background-color: white;
            border: 1px solid #e5e5ea;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            color: #1c1c1e;
        }
        QLineEdit:focus {
            border: 1px solid #8e8e93;
            outline: none;
        }
    """,
    'note_search': """
        QLineEdit {
            background-color: white;
            border: 1px solid #d1d1d6;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            color: #1c1c1e;
        }
        QLineEdit:focus {
            border: 1px solid #8e8e93;
            outline: none;
        }
    """,
    'notes_list': """
        QListWidget {
            background-color: transparent;
            border: none;
            outline: none;
        }
        QListWidget::item {
            padding: 0;
            border-bottom: 1px solid #e5e5ea;
            background-color: transparent;
            margin: 0;
        }
        QListWidget::item:hover {
            background-color: transparent;
        }
        QListWidget::item:selected {
            background-color: #e5e5ea;
        }
        QListWidget::item:selected * {
            color: #1c1c1e;
            background-color: transparent;
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #c7c7cc;
            border-radius: 4px;
            min-height: 20px;
            margin: 2px 0px;
        }
        QScrollBar::handle:vertical:hover {
            background: #aeaeb2;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """,
    'toolbar': """
        QWidget {
            background-color: white;
            border-bottom: 1px solid #d1d1d6;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
    """,
    'toolbar_btn': """
        QPushButton {
            background-color: transparent;
            border: none;
            border-radius: 6px;
            color: #3a3a3c;
            padding: 0px;
            min-width: 36px;
            min-height: 36px;
        }
        QPushButton:hover {
            background-color: #e5e5ea;
        }
        QPushButton:checked {
            background-color: #3a3a3c;
            color: white;
        }
        QPushButton:pressed {
            background-color: #c7c7cc;
        }
    """,
    'title_input': """
        QLineEdit {
            border: none;
            background-color: transparent;
            padding: 0;
            font-size: 28px;
            font-weight: bold;
            color: #1c1c1e;
        }
        QLineEdit:focus {
            outline: none;
        }
        QLineEdit::placeholder {
            color: #aeaeb2;
        }
    """,
    'date_label': """
        QLabel {
            color: #aeaeb2;
            font-size: 11px;
            padding: 0;
            border-bottom: 1px solid #e5e5ea;
        }
    """,
    'editor': """
        QTextEdit {
            border: none;
            background-color: transparent;
            line-height: 1.6;
            color: #1c1c1e;
            selection-background-color: #c7c7cc;
            selection-color: #1c1c1e;
        }
        QTextEdit:focus {
            outline: none;
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 0px;
        }
    """,
    'menubar': """
        QMenuBar {
            background-color: white;
            border-bottom: 1px solid #d1d1d6;
            color: #1c1c1e;
        }
        QMenuBar::item {
            padding: 8px 16px;
            color: #1c1c1e;
        }
        QMenuBar::item:selected {
            background-color: #e5e5ea;
        }
    """,
    'note_item_title': 'color: #1c1c1e; background: transparent;',
    'note_item_preview': 'color: #8e8e93; background: transparent;',
    'note_item_date': 'color: #aeaeb2; background: transparent;',
}


# =================================================================
# 自定义组件
# =================================================================

class NoteListWidget(QListWidget):
    """自定义笔记列表部件，支持拖动排序"""
    
    note_delete_requested = pyqtSignal(int)  # 删除请求信号
    note_order_changed = pyqtSignal(list)     # 顺序变化信号
    note_pin_requested = pyqtSignal(int)      # 置顶请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 启用拖放功能
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
    
    def startDrag(self, supportedActions):
        """开始拖动时，创建自定义的拖动视觉效果"""
        # 获取当前选中的item
        item = self.currentItem()
        if not item:
            return
        
        # 获取对应的widget
        widget = self.itemWidget(item)
        if not widget:
            return super().startDrag(supportedActions)
        
        # 创建拖动对象
        drag = QDrag(self)
        
        # 创建带背景的pixmap
        size = widget.size()
        pixmap = QPixmap(size)
        
        # 填充白色背景
        pixmap.fill(Qt.GlobalColor.white)
        
        # 使用QPainter绘制内容，确保视觉效果正确
        from PyQt6.QtGui import QPainter
        painter = QPainter(pixmap)
        
        # 绘制widget到pixmap
        widget.render(painter)
        painter.end()
        
        # 设置拖动 pixmap
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        
        # 创建mime数据
        mime_data = self.mimeData([item])
        drag.setMimeData(mime_data)
        
        # 执行拖动
        drag.exec(supportedActions)
    
    def dropEvent(self, event):
        """处理放置事件，实现拖动排序"""
        # 保存原始顺序的ID列表
        original_ids = []
        for i in range(self.count()):
            item = self.item(i)
            if item:
                original_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # 执行默认的放置操作
        super().dropEvent(event)
        
        # 获取新的顺序
        new_ids = []
        for i in range(self.count()):
            item = self.item(i)
            if item:
                new_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # 如果顺序发生了变化，发射信号
        if original_ids != new_ids:
            self.note_order_changed.emit(new_ids)


class NoteListItem(QWidget):
    """自定义笔记列表项组件"""
    
    delete_clicked = None  # 删除信号
    pin_clicked = None     # 置顶信号
    
    def __init__(self, title, preview, date_text, is_pinned=False, parent=None):
        super().__init__(parent)
        self.is_pinned = is_pinned  # 保存置顶状态
        # 设置背景色，确保拖动时有底色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)
        self._setup_ui(title, preview, date_text, is_pinned)
    
    def _setup_ui(self, title, preview, date_text, is_pinned=False):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(2)
        
        # 标题行容器（水平布局：标题 + 置顶按钮 + 省略号按钮）
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # 标题标签
        self.title_label = QLabel(title or tr('untitled'))
        self.title_label.setFont(QFont(*FONTS['title']))
        self.title_label.setStyleSheet(STYLES['note_item_title'])
        self.title_label.setWordWrap(False)
        self.title_label.setMaximumHeight(18)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_layout.addWidget(self.title_label)
        
        # 置顶按钮
        self.pin_btn = QPushButton("📌" if is_pinned else "📍")
        self.pin_btn.setFont(QFont("Arial", 10))
        self.pin_btn.setFixedSize(20, 16)
        self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pin_color = "#ff3b30" if is_pinned else "#aeaeb2"
        self.pin_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {pin_color};
                padding: 0px;
            }}
            QPushButton:hover {{
                color: #ff3b30;
            }}
        """)
        self.pin_btn.clicked.connect(self._handle_pin)
        title_layout.addWidget(self.pin_btn)
        
        # 省略号按钮
        self.more_btn = QPushButton("•••")
        self.more_btn.setFont(QFont("Arial", 10))
        self.more_btn.setFixedSize(20, 16)
        self.more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.more_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #aeaeb2;
                padding: 0px;
            }
            QPushButton:hover {
                color: #8e8e93;
            }
        """)
        self.more_btn.clicked.connect(self._show_delete_menu)
        title_layout.addWidget(self.more_btn)
        
        layout.addWidget(title_container)
        
        # 预览标签
        self.preview_label = QLabel(preview or "")
        self.preview_label.setFont(QFont(*FONTS['preview']))
        self.preview_label.setStyleSheet(STYLES['note_item_preview'])
        self.preview_label.setWordWrap(False)
        self.preview_label.setMaximumHeight(16)
        layout.addWidget(self.preview_label)
        
        # 日期标签
        self.date_label = QLabel(date_text)
        self.date_label.setFont(QFont(*FONTS['date']))
        self.date_label.setStyleSheet(STYLES['note_item_date'])
        layout.addWidget(self.date_label)
    
    def _show_delete_menu(self):
        """显示删除菜单"""
        from PyQt6.QtWidgets import QMenu
        
        # 获取按钮的全局位置
        pos = self.more_btn.mapToGlobal(self.more_btn.rect().bottomRight())
        pos.setX(pos.x() - 80)  # 向左偏移，使菜单位置更合适
        
        # 创建菜单
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: none;
                padding: 8px 0px;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #1c1c1e;
            }
            QMenu::item:selected {
                background-color: #e5e5ea;
            }
        """)
        
        # 添加删除选项
        delete_action = QAction(tr('menu_delete'), self)
        delete_action.triggered.connect(self._handle_delete)
        menu.addAction(delete_action)
        
        # 设置圆角裁剪
        from PyQt6.QtGui import QPainter, QRegion
        from PyQt6.QtCore import QRect
        menu.resize(100, 40)  # 设置初始大小
        rounded_region = QRegion(menu.rect(), QRegion.RegionType.Rectangle)
        menu.setMask(rounded_region)
        
        # 显示菜单
        menu.exec(pos)
    
    def _handle_pin(self):
        """处理置顶"""
        # 获取父级容器
        container = self.parent()
        if container and container.parent():
            # 获取列表部件
            list_widget = container.parent()
            if hasattr(list_widget, 'count'):
                # 找到列表项
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if list_widget.itemWidget(item) == self:
                        # 发射信号通知主窗口
                        if hasattr(list_widget, 'note_pin_requested'):
                            list_widget.note_pin_requested.emit(i)
                        break
    
    def _handle_delete(self):
        """处理删除"""
        # 获取父级容器
        container = self.parent()
        if container and container.parent():
            # 获取列表部件
            list_widget = container.parent()
            if hasattr(list_widget, 'count'):
                # 找到列表项
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if list_widget.itemWidget(item) == self:
                        # 发射信号通知主窗口
                        list_widget.note_delete_requested.emit(i)
                        break
    
    def update_content(self, title, preview, date_text):
        """更新内容"""
        self.title_label.setText(title or tr('untitled'))
        self.preview_label.setText(preview or "")
        self.date_label.setText(date_text)
    
    def update_pin_status(self, is_pinned):
        """更新置顶状态"""
        self.is_pinned = is_pinned
        self.pin_btn.setText("📌" if is_pinned else "📍")
        pin_color = "#ff3b30" if is_pinned else "#aeaeb2"
        self.pin_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {pin_color};
                padding: 0px;
            }}
            QPushButton:hover {{
                color: #ff3b30;
            }}
        """)


# =================================================================
# 主应用类
# =================================================================

class NotesApp(QMainWindow):
    """笔记应用主窗口"""
    
    def __init__(self):
        super().__init__()
        self.notes = []
        self.current_note_index = -1
        # self.current_font_size = DEFAULT_FONT_SIZE  # 字体大小功能暂时注释（待修复）
        
        # 搜索功能相关变量
        self.search_match_count = 0  # 搜索匹配项总数
        self.search_current_index = 0  # 当前选中的匹配项索引
        # 获取应用程序所在目录（兼容打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的 exe，使用 exe 所在目录
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_dir = app_dir
        self.db_path = os.path.join(app_dir, "notes.db")
        self._init_database()
        self.init_ui()
        self.load_notes()
    
    # ----------------------------------------------------------------
    # 数据库初始化
    # ----------------------------------------------------------------
    
    def _init_database(self):
        """初始化数据库并自动迁移JSON数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_pinned INTEGER NOT NULL DEFAULT 0,
                pinned_at TEXT
            )
        ''')
        
        # 检查并添加新字段（兼容旧数据库）
        try:
            cursor.execute("SELECT is_pinned FROM notes LIMIT 1")
        except sqlite3.OperationalError:
            # 字段不存在，添加字段
            cursor.execute("ALTER TABLE notes ADD COLUMN is_pinned INTEGER NOT NULL DEFAULT 0")
            cursor.execute("ALTER TABLE notes ADD COLUMN pinned_at TEXT")
            conn.commit()
        
        # 检查是否需要迁移JSON数据
        cursor.execute("SELECT COUNT(*) FROM notes")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 尝试从JSON文件迁移数据
            json_path = os.path.join(self.app_dir, "notes_data.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        old_notes = json.load(f)
                    
                    for note in old_notes:
                        cursor.execute('''
                            INSERT INTO notes (title, content, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            note.get("title", ""),
                            note.get("content", ""),
                            note.get("created_at", datetime.now().isoformat()),
                            note.get("updated_at", datetime.now().isoformat())
                        ))
                    
                    conn.commit()
                    print("Data migrated from JSON to SQLite successfully!")
                except Exception as e:
                    print(f"Error migrating data: {e}")
        
        conn.close()
    
    # ----------------------------------------------------------------
    # UI初始化
    # ----------------------------------------------------------------
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("WinNote")
        self.setGeometry(100, 100, 1200, 800)
        QApplication.setStyle(QStyleFactory.create("macOS"))
        
        # 设置窗口图标
        self._set_window_icon()
        
        # 中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(STYLES['main'])
        
        # 主布局
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._create_sidebar()
        self._create_editor_area()
        self.create_menu_bar()
        
        # 添加 Ctrl+F 快捷键
        self.search_shortcut = QAction(self)
        self.search_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        self.search_shortcut.triggered.connect(self.show_search_box)
        self.addAction(self.search_shortcut)
    
    def _set_window_icon(self):
        """设置窗口图标 - 生成一个简洁的笔记图标"""
        try:
            # 创建图标
            icon_size = 64
            icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # 绘制圆角矩形背景 (macOS 灰色风格)
            margin = 4
            draw.rounded_rectangle(
                [margin, margin, icon_size - margin - 1, icon_size - margin - 1],
                radius=12,
                fill=(60, 60, 62, 255)  # 深灰色 accent
            )
            
            # 绘制"便签"图案 - 简化的线条表示文字
            line_color = (255, 255, 255, 230)
            line_start_y = 22
            line_spacing = 8
            for i in range(3):
                line_width = 28 if i == 0 else 24  # 第一行稍长
                draw.line(
                    [(16, line_start_y + i * line_spacing), 
                     (16 + line_width, line_start_y + i * line_spacing)],
                    fill=line_color,
                    width=3
                )
            
            # 转换为 Qt 图标
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            icon.save(buffer, format='PNG')
            buffer.close()
            
            qicon = QIcon()
            qicon.addPixmap(QPixmap.fromImage(QImage.fromData(buffer.data())))
            
            # 设置应用图标和窗口图标
            QApplication.setWindowIcon(qicon)
            self.setWindowIcon(qicon)
            
        except Exception as e:
            print(f"图标设置失败: {e}")
    
    def _create_sidebar(self):
        """创建左侧边栏"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)
        self.sidebar.setStyleSheet(STYLES['sidebar'])
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # 搜索框
        self._create_search_box()
        
        # 笔记列表
        self._create_notes_list()
        
        self.main_layout.addWidget(self.sidebar)
    
    def _create_search_box(self):
        """创建搜索框"""
        container = QWidget()
        container.setFixedHeight(60)
        container.setStyleSheet(STYLES['search_container'])
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 8)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(tr('placeholder_search'))
        self.search_box.setStyleSheet(STYLES['search_box'])
        self.search_box.textChanged.connect(self.filter_notes)
        
        layout.addWidget(self.search_box)
        self.sidebar_layout.addWidget(container)
    
    def _create_notes_list(self):
        """创建笔记列表"""
        self.notes_list = NoteListWidget()
        self.notes_list.setStyleSheet(STYLES['notes_list'])
        self.notes_list.itemClicked.connect(self.select_note)
        self.notes_list.note_delete_requested.connect(self.delete_note_by_index)
        self.notes_list.note_order_changed.connect(self._handle_order_changed)
        self.notes_list.note_pin_requested.connect(self.toggle_pin)
        self.sidebar_layout.addWidget(self.notes_list)
    
    def _handle_order_changed(self, new_order_ids):
        """处理笔记顺序变化"""
        # 根据新的ID顺序重新排列 notes 列表
        notes_dict = {note["id"]: note for note in self.notes}
        self.notes = [notes_dict[note_id] for note_id in new_order_ids if note_id in notes_dict]
        
        # 更新数据库中的顺序（更新 updated_at 以触发重新排序）
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for note in self.notes:
            cursor.execute('''
                UPDATE notes SET updated_at = ? WHERE id = ?
            ''', (note["updated_at"], note["id"]))
        conn.commit()
        conn.close()
    
    def _create_editor_area(self):
        """创建编辑器区域"""
        self.editor_area = QWidget()
        self.editor_area.setStyleSheet("""
            background-color: white;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        """)
        
        self.editor_layout = QVBoxLayout(self.editor_area)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)
        
        self._create_toolbar()
        self._create_editor_content()
        
        self.main_layout.addWidget(self.editor_area, 1)
    
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QWidget()
        self.toolbar.setFixedHeight(TOOLBAR_HEIGHT)
        self.toolbar.setStyleSheet(STYLES['toolbar'])
        
        # 按钮容器
        button_container = QWidget(self.toolbar)
        button_container.setFixedHeight(36)
        button_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #3a3a3c;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e5e5ea;
            }
            QPushButton:checked {
                background-color: #3a3a3c;
                color: white;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        button_layout.addStretch()
        
        # 格式化按钮
        self.bold_btn = self._create_toolbar_button("B", 'bold')
        self.italic_btn = self._create_toolbar_button("I", 'italic')
        self.strikethrough_btn = self._create_toolbar_button("S", 'strikethrough')
        
        button_layout.addWidget(self.bold_btn)
        button_layout.addWidget(self.italic_btn)
        button_layout.addWidget(self.strikethrough_btn)
        
        # # 添加分隔符
        # separator = QFrame()
        # separator.setFrameShape(QFrame.Shape.VLine)
        # separator.setStyleSheet("border: none; background-color: #d1d1d6; max-width: 1px; margin: 8px 12px;")
        # button_layout.addWidget(separator)
        
        # # 字体大小按钮
        # self.font_decrease_btn = self._create_font_size_button("A-", 'decrease')
        # self.font_increase_btn = self._create_font_size_button("A+", 'increase')
        
        # button_layout.addWidget(self.font_decrease_btn)
        # button_layout.addWidget(self.font_increase_btn)
        
        button_layout.addStretch()
        
        # 垂直居中
        container_layout = QVBoxLayout(self.toolbar)
        container_layout.setContentsMargins(16, 4, 16, 4)
        container_layout.addWidget(button_container, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.editor_layout.addWidget(self.toolbar)
    
    def _create_toolbar_button(self, text, format_type):
        """创建工具栏按钮"""
        btn = QPushButton(text)
        btn.setFont(QFont(*FONTS['toolbar']))
        btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # 样式由父容器设置，这里不再单独设置
        
        # 设置鼠标悬停提示
        if format_type == 'bold':
            btn.setToolTip(tr('tooltip_bold'))
        elif format_type == 'italic':
            btn.setToolTip(tr('tooltip_italic'))
        elif format_type == 'strikethrough':
            btn.setToolTip(tr('tooltip_strikethrough'))
        
        # 特殊样式
        if format_type == 'italic':
            btn.setStyleSheet(STYLES['toolbar_btn'] + "font-style: italic;")
        elif format_type == 'strikethrough':
            btn.setStyleSheet(STYLES['toolbar_btn'] + "text-decoration: line-through;")
        
        # 信号连接
        if format_type == 'bold':
            btn.clicked.connect(lambda checked: self.toggle_format('bold', checked))
        elif format_type == 'italic':
            btn.clicked.connect(lambda checked: self.toggle_format('italic', checked))
        elif format_type == 'strikethrough':
            btn.clicked.connect(lambda checked: self.toggle_format('strikethrough', checked))
        
        return btn
    
    # # 字体大小功能暂时注释（待修复）
    # def _create_font_size_button(self, text, action):
    #     """创建字体大小按钮"""
    #     btn = QPushButton(text)
    #     btn.setFont(QFont(*FONTS['toolbar']))
    #     btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
    #     btn.setCursor(Qt.CursorShape.PointingHandCursor)
    #     btn.setStyleSheet(STYLES['toolbar_btn'])
    #     
    #     # 设置鼠标悬停提示
    #     if action == 'increase':
    #         btn.setToolTip(tr('tooltip_font_increase'))
    #     elif action == 'decrease':
    #         btn.setToolTip(tr('tooltip_font_decrease'))
    #     
    #     # 信号连接
    #     if action == 'increase':
    #         btn.clicked.connect(self.increase_font_size)
    #     elif action == 'decrease':
    #         btn.clicked.connect(self.decrease_font_size)
    #     
    #     return btn
    # 
    # def increase_font_size(self):
    #     """增大字体大小"""
    #     if self.current_font_size < MAX_FONT_SIZE:
    #         self.current_font_size += 1
    #         self._update_editor_font()
    # 
    # def decrease_font_size(self):
    #     """减小字体大小"""
    #     if self.current_font_size > MIN_FONT_SIZE:
    #         self.current_font_size -= 1
    #         self._update_editor_font()
    # 
    # def _update_editor_font(self):
    #     """更新编辑器字体大小"""
    #     # 创建新字体
    #     new_font = QFont(*FONTS['editor'])
    #     new_font.setPointSize(self.current_font_size)
    #     
    #     # 更新编辑器字体
    #     self.editor.setFont(new_font)
    #     
    #     # 更新文档默认样式
    #     cursor = self.editor.textCursor()
    #     if cursor.hasSelection():
    #         # 如果有选中文本，只更新选中文本的字体
    #         pass
    #     else:
    #         # 更新整个文档的默认字体
    #         self.editor.document().setDefaultFont(new_font)
    #     
    #     # 恢复焦点
    #     self.editor.setFocus()
    #     self.editor.viewport().update()
    
    def _create_editor_content(self):
        """创建编辑器内容区域"""
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(80, 40, 80, 40)
        self.content_layout.setSpacing(16)
        
        # 标题输入
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(tr('placeholder_title'))
        self.title_input.setFont(QFont(*FONTS['editor_title']))
        self.title_input.setStyleSheet(STYLES['title_input'])
        self.title_input.textChanged.connect(self.update_title)
        self.content_layout.addWidget(self.title_input)
        
        # 日期标签
        self.date_label = QLabel()
        self.date_label.setStyleSheet(STYLES['date_label'])
        self.content_layout.addWidget(self.date_label)
        
        # 文本编辑器
        self.editor = QTextEdit()
        self.editor.setFont(QFont(*FONTS['editor']))
        self.editor.setStyleSheet(STYLES['editor'])
        self.editor.textChanged.connect(self._handle_editor_change)
        self.editor.currentCharFormatChanged.connect(self.update_format_indicators)
        self.content_layout.addWidget(self.editor, 1)
        
        # 搜索框容器（悬浮显示在右上角，默认隐藏）
        self.search_container = QWidget(self.content_widget)  # 设置父容器
        self.search_container.setFixedSize(280, 36)
        self.search_container.setVisible(False)  # 默认隐藏
        
        # 搜索框内部布局
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(6, 4, 6, 4)
        search_layout.setSpacing(4)
        
        # 搜索框
        self.note_search_box = QLineEdit()
        self.note_search_box.setPlaceholderText(tr('placeholder_note_search'))
        self.note_search_box.setFixedWidth(180)
        self.note_search_box.setStyleSheet(STYLES['note_search'])
        self.note_search_box.textChanged.connect(self.highlight_search)
        self.note_search_box.returnPressed.connect(self.find_next)
        
        # 匹配数量标签
        self.search_count_label = QLabel()
        self.search_count_label.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 12px;
                padding: 0px;
                background-color: transparent;
            }
        """)
        self.search_count_label.setFixedWidth(30)
        self.search_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 关闭按钮
        self.search_close_btn = QPushButton("✕")
        self.search_close_btn.setFixedSize(20, 20)
        self.search_close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e93;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #1c1c1e;
            }
        """)
        self.search_close_btn.clicked.connect(self.hide_search_box)
        
        search_layout.addWidget(self.note_search_box)
        search_layout.addWidget(self.search_count_label)
        search_layout.addWidget(self.search_close_btn)
        
        # 容器样式（带边框的白色背景，阴影效果）
        self.search_container.setStyleSheet("""
            background-color: white;
            border: 1px solid #d1d1d6;
            border-radius: 8px;
        """)
        
        self.editor_layout.addWidget(self.content_widget)
    
    def _handle_editor_change(self):
        """处理编辑器内容变化"""
        self.update_note()
    
    # ----------------------------------------------------------------
    # 笔记搜索功能
    # ----------------------------------------------------------------
    
    def show_search_box(self):
        """显示/隐藏搜索框"""
        if self.search_container.isVisible():
            # 搜索框已经显示，关闭它
            self.hide_search_box()
        else:
            # 显示搜索框（设置在右上角悬浮）
            self.search_container.setVisible(True)
            self.search_container.raise_()  # 提升到最上层
            
            # 计算搜索框位置（右上角）
            # 使用 QWidget 的 geometry 来设置位置
            content_rect = self.content_widget.geometry()
            search_x = content_rect.width() - self.search_container.width() - 10  # 右边距 10px
            search_y = 0  # 顶部
            self.search_container.move(search_x, search_y)
            
            self.note_search_box.clear()
            self.note_search_box.setFocus()
            self.highlight_search("")
    
    def hide_search_box(self):
        """隐藏搜索框"""
        self.note_search_box.clear()
        self.search_count_label.setText("")  # 清除计数标签
        self.highlight_search("")  # 清除高亮
        self.search_container.setVisible(False)  # 隐藏搜索框
        self.search_match_count = 0
        self.search_current_index = 0
        self.editor.setFocus()
    
    def highlight_search(self, text):
        """高亮搜索结果"""
        # 清除所有现有的高亮格式
        self._clear_search_highlight()
        
        # 恢复默认格式 - 移动光标到开头清除选择
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        
        if not text:
            self.search_match_count = 0
            self.search_current_index = 0
            self.search_count_label.setText("")  # 清除计数标签
            self.note_search_box.setPlaceholderText(tr('placeholder_note_search'))
            return
        
        try:
            # 使用正则表达式实现大小写不敏感搜索
            import re
            pattern = re.compile(re.escape(text), re.IGNORECASE)
            
            # 获取文档文本
            document = self.editor.document()
            text_content = document.toPlainText()
            
            # 设置高亮颜色
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(Qt.GlobalColor.yellow)
            
            # 找到所有匹配项并高亮
            match_list = list(pattern.finditer(text_content))
            self.search_match_count = len(match_list)
            self.search_current_index = 0
            
            for match in match_list:
                start_pos = match.start()
                end_pos = match.end()
                
                # 创建光标并选择匹配文本
                cursor = QTextCursor(document)
                cursor.setPosition(start_pos)
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, end_pos - start_pos)
                cursor.mergeCharFormat(highlight_format)
            
            # 更新计数标签显示匹配数量
            if self.search_match_count > 0:
                self.search_count_label.setText(f"0/{self.search_match_count}")
            else:
                self.search_count_label.setText("")
            
            # 回到开头
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            
        except Exception as e:
            print(f"搜索错误: {e}")
    
    def _clear_search_highlight(self):
        """清除所有搜索高亮（保留其他文本格式）"""
        document = self.editor.document()
        
        # 创建一个只设置背景色的格式（透明），其他格式保持不变
        cursor = document.find("")  # 创建一个空的光标
        cursor = QTextCursor(document)
        
        # 遍历文档所有块
        block = document.begin()
        while block.isValid():
            block_cursor = QTextCursor(block)
            block_cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            
            # 只清除背景色，不改变其他格式
            clear_format = QTextCharFormat()
            clear_format.setBackground(Qt.GlobalColor.transparent)
            block_cursor.mergeCharFormat(clear_format)
            
            block = block.next()
        
        # 同时处理文档末尾可能的额外内容
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        
        # 只清除背景色
        clear_format = QTextCharFormat()
        clear_format.setBackground(Qt.GlobalColor.transparent)
        cursor.mergeCharFormat(clear_format)
    
    def find_next(self):
        """查找下一个"""
        text = self.note_search_box.text()
        if text and self.search_match_count > 0:
            try:
                # 使用正则表达式查找下一个匹配项
                import re
                pattern = re.compile(re.escape(text), re.IGNORECASE)
                
                # 获取当前光标位置之后的文本
                document = self.editor.document()
                cursor = self.editor.textCursor()
                current_pos = cursor.position()
                text_content = document.toPlainText()
                remaining_text = text_content[current_pos:]
                
                # 在剩余文本中查找
                match = pattern.search(remaining_text)
                if match:
                    # 找到，跳转到该位置
                    new_pos = current_pos + match.start()
                    cursor.setPosition(new_pos)
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(text))
                    self.editor.setTextCursor(cursor)
                    # 更新当前索引
                    self.search_current_index = (self.search_current_index + 1) % self.search_match_count
                else:
                    # 没找到，回到开头继续找
                    cursor = self.editor.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    self.editor.setTextCursor(cursor)
                    
                    # 再次尝试在全文中查找
                    full_match = pattern.search(text_content)
                    if full_match:
                        cursor.setPosition(full_match.start())
                        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(text))
                        self.editor.setTextCursor(cursor)
                        # 更新当前索引
                        self.search_current_index = 1
                
                # 更新计数标签显示当前索引
                self.search_count_label.setText(f"{self.search_current_index}/{self.search_match_count}")
                
            except Exception as e:
                print(f"查找错误: {e}")
    
    def resizeEvent(self, event):
        """窗口大小改变时更新搜索框位置"""
        super().resizeEvent(event)
        # 如果搜索框可见，更新其位置
        if hasattr(self, 'search_container') and self.search_container.isVisible():
            content_rect = self.content_widget.geometry()
            search_x = content_rect.width() - self.search_container.width() - 10
            search_y = 0
            self.search_container.move(search_x, search_y)
    
    # ----------------------------------------------------------------
    # 菜单栏
    # ----------------------------------------------------------------
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        menubar.setStyleSheet(STYLES['menubar'])
        
        # 文件菜单
        file_menu = menubar.addMenu(tr('menu_file'))
        
        new_action = QAction(tr('menu_new_note'), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_note)
        file_menu.addAction(new_action)
        
        delete_action = QAction(tr('menu_delete'), self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_note)
        file_menu.addAction(delete_action)
        
        # 语言菜单
        language_menu = menubar.addMenu(tr('menu_language'))
        self.language_group = []
        
        for lang_code, lang_name in LANGUAGES.items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setData(lang_code)
            if lang_code == current_language:
                action.setChecked(True)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            language_menu.addAction(action)
            self.language_group.append(action)
        
        # 帮助菜单
        help_menu = menubar.addMenu(tr('menu_help'))
        
        about_action = QAction(tr('menu_about'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('about_title'))
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f2f2f7;
            }
            QLabel {
                background-color: transparent;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用名称
        title_label = QLabel("WinNote")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1c1c1e;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # 版本号
        version_label = QLabel(f"{tr('about_version')} {VERSION}")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #8e8e93;
                background-color: transparent;
            }
        """)
        layout.addWidget(version_label)
        
        # 描述
        desc_label = QLabel(tr('about_description'))
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #3a3a3c;
                background-color: transparent;
                padding-top: 15px;
            }
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # 作者信息
        author_label = QLabel(tr('about_author'))
        author_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #aeaeb2;
                background-color: transparent;
                padding-top: 10px;
            }
        """)
        layout.addWidget(author_label)
        
        dialog.exec()
    
    def change_language(self, lang_code):
        """切换语言"""
        set_language(lang_code)
        
        # 更新菜单栏
        self.menuBar().clear()
        self.create_menu_bar()
        
        # 更新搜索框placeholder
        self.search_box.setPlaceholderText(tr('placeholder_search'))
        
        # 更新标题输入框placeholder
        self.title_input.setPlaceholderText(tr('placeholder_title'))
        
        # 更新工具栏提示
        self.bold_btn.setToolTip(tr('tooltip_bold'))
        self.italic_btn.setToolTip(tr('tooltip_italic'))
        self.strikethrough_btn.setToolTip(tr('tooltip_strikethrough'))
        
        # 更新笔记列表
        self.update_notes_list()
    
    # ----------------------------------------------------------------
    # 格式化功能
    # ----------------------------------------------------------------
    
    def toggle_format(self, format_type, checked):
        """切换文本格式"""
        format = QTextCharFormat()
        
        if format_type == 'bold':
            format.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
            self.bold_btn.setChecked(checked)
        elif format_type == 'italic':
            format.setFontItalic(checked)
            self.italic_btn.setChecked(checked)
        elif format_type == 'strikethrough':
            format.setFontStrikeOut(checked)
            self.strikethrough_btn.setChecked(checked)
        
        self.editor.mergeCurrentCharFormat(format)
        # 恢复编辑器焦点，避免光标消失
        self.editor.setFocus()
        self.editor.viewport().update()
    
    def update_format_indicators(self, format):
        """更新格式指示器状态"""
        self.bold_btn.setChecked(format.font().bold())
        self.italic_btn.setChecked(format.font().italic())
        self.strikethrough_btn.setChecked(format.fontStrikeOut())
    
    # ----------------------------------------------------------------
    # 工具方法
    # ----------------------------------------------------------------
    
    def get_preview_text(self, content, max_length=PREVIEW_MAX_LENGTH):
        """获取预览文本"""
        doc = QTextDocument()
        doc.setHtml(content)
        text = doc.toPlainText().strip()
        text = ' '.join(text.split())
        
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text if text else ""
    
    def format_date(self, iso_date):
        """格式化日期显示"""
        try:
            dt = datetime.fromisoformat(iso_date)
            now = datetime.now()
            
            if dt.date() == now.date():
                return dt.strftime("%#I:%M %p").strip()
            elif dt.year == now.year:
                return dt.strftime("%B %d")
            else:
                return dt.strftime("%B %d, %Y")
        except:
            return ""
    
    # ----------------------------------------------------------------
    # 笔记操作
    # ----------------------------------------------------------------
    
    def new_note(self):
        """创建新笔记"""
        now = datetime.now()
        
        # 插入数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notes (title, content, created_at, updated_at, is_pinned, pinned_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("", "", now.isoformat(), now.isoformat(), 0, None))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        note = {
            "id": note_id,
            "title": "",
            "content": "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "is_pinned": 0,
            "pinned_at": None
        }
        
        self.notes.insert(0, note)
        self.current_note_index = 0
        self.update_notes_list()
        self.title_input.setText("")
        self.editor.setPlainText("")
        self.title_input.setFocus()
        self.date_label.setText(self.format_date(now.isoformat()))
    
    def select_note(self, item):
        """选择笔记"""
        index = self.notes_list.row(item)
        if index >= 0 and index < len(self.notes):
            self.current_note_index = index
            note = self.notes[index]
            
            self.title_input.setText(note["title"])
            self.editor.setHtml(note["content"])
            self.date_label.setText(self.format_date(note["updated_at"]))
    
    def update_title(self, text):
        """更新标题"""
        if self.current_note_index >= 0 and self.current_note_index < len(self.notes):
            # 只有内容真正变化时才更新时间
            if text != self.notes[self.current_note_index]["title"]:
                self.notes[self.current_note_index]["title"] = text
                updated_at = datetime.now().isoformat()
                self.notes[self.current_note_index]["updated_at"] = updated_at
                
                # 更新数据库
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE notes SET title = ?, updated_at = ? WHERE id = ?
                ''', (text, updated_at, self.notes[self.current_note_index]["id"]))
                conn.commit()
                conn.close()
                
                self.update_notes_list_item(self.current_note_index)
                self.save_notes()

    def update_note(self):
        """更新笔记内容"""
        if self.current_note_index >= 0 and self.current_note_index < len(self.notes):
            new_content = self.editor.toHtml()
            # 只有内容真正变化时才更新时间
            if new_content != self.notes[self.current_note_index]["content"]:
                self.notes[self.current_note_index]["content"] = new_content
                updated_at = datetime.now().isoformat()
                self.notes[self.current_note_index]["updated_at"] = updated_at
                
                # 更新数据库
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE notes SET content = ?, updated_at = ? WHERE id = ?
                ''', (new_content, updated_at, self.notes[self.current_note_index]["id"]))
                conn.commit()
                conn.close()
                
                self.update_notes_list_item(self.current_note_index)
                self.date_label.setText(self.format_date(updated_at))
                self.save_notes()
    
    def delete_note(self):
        """删除笔记"""
        if self.current_note_index >= 0 and self.current_note_index < len(self.notes):
            note_id = self.notes[self.current_note_index]["id"]
            
            # 从数据库删除
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            conn.close()
            
            self.notes.pop(self.current_note_index)
            self.current_note_index = -1
            self.update_notes_list()
            self.title_input.setText("")
            self.editor.setPlainText("")
            self.date_label.setText("")
            self.save_notes()
    
    def toggle_pin(self, index):
        """切换置顶状态"""
        if index >= 0 and index < len(self.notes):
            note = self.notes[index]
            is_pinned = not note.get("is_pinned", False)
            pinned_at = datetime.now().isoformat() if is_pinned else None
            
            # 更新数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notes SET is_pinned = ?, pinned_at = ? WHERE id = ?
            ''', (1 if is_pinned else 0, pinned_at, note["id"]))
            conn.commit()
            conn.close()
            
            # 更新本地数据
            note["is_pinned"] = is_pinned
            note["pinned_at"] = pinned_at
            
            # 更新置顶按钮显示
            item_widget = self.notes_list.itemWidget(self.notes_list.item(index))
            if item_widget and hasattr(item_widget, 'update_pin_status'):
                item_widget.update_pin_status(is_pinned)
            
            # 重新排序并更新列表
            self._sort_notes()
            self.update_notes_list()
    
    def delete_note_by_index(self, index):
        """根据索引删除笔记"""
        if index >= 0 and index < len(self.notes):
            self.current_note_index = index
            self.delete_note()
    
    def filter_notes(self, text):
        """过滤笔记"""
        self.update_notes_list(text)
    
    def update_notes_list(self, filter_text=""):
        """更新笔记列表"""
        self.notes_list.clear()
        
        filtered_notes = self.notes
        if filter_text:
            filter_lower = filter_text.lower()
            filtered_notes = [
                note for note in self.notes
                if filter_lower in note["title"].lower() or 
                   filter_lower in self.get_preview_text(note["content"]).lower()
            ]
        
        for note in filtered_notes:
            preview = self.get_preview_text(note["content"])
            date_text = self.format_date(note["updated_at"])
            title = note["title"] or tr('untitled')
            is_pinned = note.get("is_pinned", 0) == 1
            
            item_widget = NoteListItem(title, preview, date_text, is_pinned)
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, note["id"])
            list_item.setSizeHint(QSize(SIDEBAR_WIDTH - 32, 80))
            
            self.notes_list.addItem(list_item)
            self.notes_list.setItemWidget(list_item, item_widget)
        
        if filtered_notes:
            self.notes_list.setCurrentRow(0)
            # 触发选中笔记，更新编辑器内容和日期
            self.select_note(self.notes_list.item(0))
    
    def update_notes_list_item(self, index):
        """更新单个列表项"""
        if 0 <= index < self.notes_list.count():
            list_item = self.notes_list.item(index)
            note = self.notes[index]
            
            preview = self.get_preview_text(note["content"])
            date_text = self.format_date(note["updated_at"])
            title = note["title"] or tr('untitled')
            is_pinned = note.get("is_pinned", 0) == 1
            
            item_widget = self.notes_list.itemWidget(list_item)
            if item_widget:
                item_widget.update_content(title, preview, date_text)
                if hasattr(item_widget, 'update_pin_status'):
                    item_widget.update_pin_status(is_pinned)
    
    # ----------------------------------------------------------------
    # 数据持久化
    # ----------------------------------------------------------------
    
    def load_notes(self):
        """从数据库加载笔记"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes")
            rows = cursor.fetchall()
            
            self.notes = []
            for row in rows:
                # 兼容旧数据库（字段可能不存在）
                is_pinned = row[5] if len(row) > 5 else 0
                pinned_at = row[6] if len(row) > 6 else None
                
                self.notes.append({
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "is_pinned": is_pinned,
                    "pinned_at": pinned_at
                })
            
            conn.close()
            
            # 排序笔记
            self._sort_notes()
            
            if not self.notes:
                self.new_note()
            else:
                self.update_notes_list()
        except Exception as e:
            print(f"加载笔记失败: {e}")
            self.new_note()
    
    def _sort_notes(self):
        """排序笔记：置顶笔记按置顶时间排序，未置顶按更新时间排序"""
        pinned_notes = []
        unpinned_notes = []
        
        for note in self.notes:
            if note.get("is_pinned", 0) == 1:
                pinned_notes.append(note)
            else:
                unpinned_notes.append(note)
        
        # 置顶笔记按置顶时间排序（最新的置顶在最上面）
        pinned_notes.sort(
            key=lambda x: x.get("pinned_at") or "",
            reverse=True
        )
        
        # 未置顶笔记按更新时间排序
        unpinned_notes.sort(
            key=lambda x: x.get("updated_at") or "",
            reverse=True
        )
        
        # 合并：置顶笔记在最上面
        self.notes = pinned_notes + unpinned_notes
    
    def save_notes(self):
        """保存笔记到数据库（保持兼容，实际操作已在各方法中完成）"""
        pass
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.save_notes()
        event.accept()


# =================================================================
# 程序入口
# =================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())
