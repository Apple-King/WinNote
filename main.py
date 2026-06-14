# =================================================================
# WinNote - Windows笔记应用
# 基于PyQt6开发的macOS Notes风格笔记客户端
# =================================================================

import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextEdit, QSplitter,
    QMessageBox, QLineEdit, QLabel, QScrollArea, QStyleFactory, QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtGui import QTextCharFormat, QAction, QFont, QTextDocument
from PyQt6.QtCore import Qt, QSize, pyqtSignal

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
    'title': ('SF Pro Text', 14, QFont.Weight.DemiBold),
    'preview': ('SF Pro Text', 11, QFont.Weight.Normal),
    'date': ('SF Pro Text', 11, QFont.Weight.Normal),
    'editor': ('SF Pro Text', 15, QFont.Weight.Normal),
    'editor_title': ('SF Pro Display', 28, QFont.Weight.Bold),
    'toolbar': ('Arial', 16, QFont.Weight.Bold),
}

# 布局常量
SIDEBAR_WIDTH = 300
TOOLBAR_HEIGHT = 44
BUTTON_SIZE = 36
PREVIEW_MAX_LENGTH = 8

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
        
        # 占位符
        'placeholder_title': 'Title',
        'placeholder_search': 'Search',
        'placeholder_editor': 'Start typing...',
        
        # 其他
        'untitled': 'Untitled',
    },
    'zh': {
        # 菜单
        'menu_file': '文件',
        'menu_new_note': '新建笔记',
        'menu_delete': '删除',
        'menu_language': '语言',
        
        # 占位符
        'placeholder_title': '标题',
        'placeholder_search': '搜索',
        'placeholder_editor': '开始输入...',
        
        # 其他
        'untitled': '无标题',
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
        }
        QPushButton:hover {
            background-color: #e5e5ea;
        }
        QPushButton:checked {
            background-color: #3a3a3c;
            color: white;
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
            font-size: 15px;
            line-height: 1.6;
            color: #1c1c1e;
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
    """自定义笔记列表部件"""
    
    note_delete_requested = pyqtSignal(int)  # 删除请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)


class NoteListItem(QWidget):
    """自定义笔记列表项组件"""
    
    delete_clicked = None  # 删除信号
    
    def __init__(self, title, preview, date_text, parent=None):
        super().__init__(parent)
        self._setup_ui(title, preview, date_text)
    
    def _setup_ui(self, title, preview, date_text):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(2)
        
        # 标题行容器（水平布局：标题 + 省略号按钮）
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


# =================================================================
# 主应用类
# =================================================================

class NotesApp(QMainWindow):
    """笔记应用主窗口"""
    
    def __init__(self):
        super().__init__()
        self.notes = []
        self.current_note_index = -1
        self.notes_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "notes_data.json"
        )
        self.init_ui()
        self.load_notes()
    
    # ----------------------------------------------------------------
    # UI初始化
    # ----------------------------------------------------------------
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Notes")
        self.setGeometry(100, 100, 1200, 800)
        QApplication.setStyle(QStyleFactory.create("macOS"))
        
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
        self.sidebar_layout.addWidget(self.notes_list)
    
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
        btn.setStyleSheet(STYLES['toolbar_btn'])
        
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
        
        self.editor_layout.addWidget(self.content_widget)
    
    def _handle_editor_change(self):
        """处理编辑器内容变化"""
        self.update_note()
    
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
        
        note = {
            "id": now.timestamp(),
            "title": "",
            "content": "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        self.notes.insert(0, note)
        self.current_note_index = 0
        self.update_notes_list()
        self.title_input.setText("")
        self.editor.setPlainText("")
        self.title_input.setFocus()
        self.date_label.setText(now.strftime("%B %d, %Y at %#I:%M %p").strip())
    
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
            self.notes[self.current_note_index]["title"] = text
            self.notes[self.current_note_index]["updated_at"] = datetime.now().isoformat()
            self.update_notes_list_item(self.current_note_index)
            self.save_notes()
    
    def update_note(self):
        """更新笔记内容"""
        if self.current_note_index >= 0 and self.current_note_index < len(self.notes):
            self.notes[self.current_note_index]["content"] = self.editor.toHtml()
            self.notes[self.current_note_index]["updated_at"] = datetime.now().isoformat()
            self.update_notes_list_item(self.current_note_index)
            self.date_label.setText(self.format_date(self.notes[self.current_note_index]["updated_at"]))
            self.save_notes()
    
    def delete_note(self):
        """删除笔记"""
        if self.current_note_index >= 0 and self.current_note_index < len(self.notes):
            self.notes.pop(self.current_note_index)
            self.current_note_index = -1
            self.update_notes_list()
            self.title_input.setText("")
            self.editor.setPlainText("")
            self.date_label.setText("")
            self.save_notes()
    
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
            
            item_widget = NoteListItem(title, preview, date_text)
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, note["id"])
            list_item.setSizeHint(QSize(SIDEBAR_WIDTH - 32, 80))
            
            self.notes_list.addItem(list_item)
            self.notes_list.setItemWidget(list_item, item_widget)
        
        if filtered_notes:
            self.notes_list.setCurrentRow(0)
    
    def update_notes_list_item(self, index):
        """更新单个列表项"""
        if 0 <= index < self.notes_list.count():
            list_item = self.notes_list.item(index)
            note = self.notes[index]
            
            preview = self.get_preview_text(note["content"])
            date_text = self.format_date(note["updated_at"])
            title = note["title"] or tr('untitled')
            
            item_widget = self.notes_list.itemWidget(list_item)
            if item_widget:
                item_widget.update_content(title, preview, date_text)
    
    # ----------------------------------------------------------------
    # 数据持久化
    # ----------------------------------------------------------------
    
    def load_notes(self):
        """加载笔记数据"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
                self.update_notes_list()
            except Exception as e:
                print(f"加载笔记失败: {e}")
                self.new_note()
        else:
            self.new_note()
    
    def save_notes(self):
        """保存笔记数据"""
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存笔记失败: {e}")
    
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
