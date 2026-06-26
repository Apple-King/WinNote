# WinNote

一个基于 PyQt6 开发的 macOS Notes 风格笔记应用，为 Windows 用户提供简洁优雅的笔记体验。

## 功能特性

- **富文本编辑**：支持加粗、斜体、删除线等文本格式化
- **macOS 风格界面**：采用 macOS Notes 的视觉设计，包含圆角、柔和阴影和灰色系配色
- **笔记列表**：左侧显示笔记列表，包含标题、预览内容和编辑时间
- **笔记内搜索**：Ctrl+F 打开悬浮搜索框，实时高亮匹配项并显示计数
- **笔记置顶**：重要笔记可置顶显示，最近置顶的排在最上面
- **拖动排序**：支持拖动笔记调整顺序
- **数据持久化**：笔记自动保存到项目目录的 SQLite 数据库
- **多语言支持**：支持中文和英文界面切换
- **响应式布局**：自适应窗口大小调整

## 技术栈

- **Python 3.8+**
- **PyQt6** - GUI 框架
- **SQLite** - 数据存储

## 安装与运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

## 打包发布

### 安装 PyInstaller

```bash
pip install pyinstaller
```

### 打包命令

**方式一：使用 spec 文件打包（推荐）**

```bash
# Windows (使用虚拟环境)
.\.venv\Scripts\python.exe -m PyInstaller main.spec

# 或直接使用 pyinstaller
pyinstaller main.spec
```

**方式二：直接命令行打包**

```bash
pyinstaller --onefile --windowed --add-data "notes.db;." main.py
```

### 打包产物

打包完成后，exe 文件位于 `dist/` 文件夹：

```
Winnote/
├── dist/
│   └── WinNote-1.0.1.exe  # 可分发的 exe 文件（版本号自动生成）
├── build/                # 临时构建文件（可删除）
├── main.py               # 源代码
├── main.spec             # 打包配置文件
├── notes.db              # SQLite 数据库文件
└── requirements.txt      # 依赖列表
```

### 注意事项

1. **首次运行**：打包后的 exe 首次运行时会自动在同目录生成 `notes.db`
2. **数据存储**：笔记数据保存在 exe 所在目录的 `notes.db` SQLite 数据库中
3. **清理临时文件**：打包完成后可删除 `build` 和 `__pycache__` 文件夹
4. **多语言支持**：打包后的 exe 完整包含中英文界面

### 常见问题

**Q: 打包后笔记无法保存？**
A: 请确保 exe 有写入权限，数据文件会保存在 exe 所在目录。

**Q: 如何查看打包错误信息？**
A: 去掉 `--windowed` 参数重新打包，会显示控制台窗口。

## 界面预览

应用包含以下主要组件：

1. **左侧边栏**：笔记列表，显示笔记标题、正文预览（前8个字符）和最后编辑时间
2. **右侧编辑区**：富文本编辑器，支持标题和正文编辑
3. **工具栏**：格式化按钮（加粗、斜体、删除线）
4. **菜单栏**：文件操作和语言切换
5. **悬浮搜索框**：Ctrl+F 打开，带边框设计，悬浮在编辑区右上角

## 使用说明

### 创建笔记
- 点击菜单栏 `文件 > 新建笔记` 或使用快捷键创建新笔记
- 新笔记包含标题输入框（带占位符提示）和正文编辑区

### 编辑笔记
- 在右侧编辑区输入标题和正文
- 使用工具栏按钮进行文本格式化：
  - **B**：加粗
  - *I*：斜体
  - ~S~：删除线

### 笔记内搜索
- 按 `Ctrl+F` 打开悬浮搜索框
- 输入关键词，自动高亮所有匹配项（黄色背景）
- 搜索框显示匹配计数（如 `0/3`、`1/3`）
- 按 `Enter` 跳转到下一个匹配项
- 再次按 `Ctrl+F` 或点击 ✕ 关闭搜索框

### 笔记置顶
- 点击笔记项右侧的置顶按钮
- 置顶的笔记会显示在列表最上方
- 多次置顶时，最近置顶的笔记排在最上面

### 拖动排序
- 鼠标拖动笔记项可以调整顺序
- 置顶笔记始终在普通笔记上方

### 删除笔记
- 选中笔记后，点击笔记项右侧的删除按钮删除笔记

### 切换语言
- 在菜单栏 `语言` 中选择中文或英文

## 项目结构

```
Winnote/
├── main.py              # 主应用代码
├── notes.db             # SQLite 数据库存储
├── migrate_json_to_sqlite.py  # JSON 数据迁移脚本
├── requirements.txt     # 依赖列表
└── README.md            # 项目说明
```

## 快捷键

- **Ctrl+F**：打开/关闭笔记内搜索
- **Ctrl+B**：加粗
- **Ctrl+I**：斜体
- **Ctrl+S**：删除线

## 开发

### 代码结构

应用采用模块化设计，主要组件包括：

- `NotesApp`：主窗口类，管理整体布局和状态
- `NoteListWidget`：笔记列表组件
- `NoteListItem`：单个笔记项组件
- `COLORS`：全局颜色配置
- `FONTS`：全局字体配置
- `TRANSLATIONS`：多语言翻译字典
- `STYLES`：Qt Style Sheets 样式配置

### 自定义样式

应用使用 Qt Style Sheets 实现自定义外观，可以通过修改 `COLORS`、`FONTS` 和 `STYLES` 常量来自定义主题。

## 数据迁移

如果从旧版本升级，可以使用 `migrate_json_to_sqlite.py` 脚本迁移历史数据：

```bash
python migrate_json_to_sqlite.py
```

## 许可证

MIT License

## 致谢

本项目参考了 macOS Notes 的界面设计风格，为 Windows 用户提供类似的使用体验。
