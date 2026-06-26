#!/usr/bin/env python3
"""
迁移脚本：将 JSON 数据迁移到 SQLite
使用方法：python migrate_json_to_sqlite.py
"""

import json
import os
import sqlite3
from datetime import datetime

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 文件路径
    json_path = os.path.join(script_dir, "notes_data.json")
    db_path = os.path.join(script_dir, "notes.db")
    
    # 检查 JSON 文件是否存在
    if not os.path.exists(json_path):
        print("错误：未找到 notes_data.json 文件")
        input("按回车键退出...")
        return
    
    # 读取 JSON 数据
    print("正在读取 JSON 数据...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        print(f"找到 {len(notes)} 条笔记")
    except Exception as e:
        print(f"读取 JSON 文件失败: {e}")
        input("按回车键退出...")
        return
    
    # 创建数据库连接
    print("正在连接数据库...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（包含置顶字段）
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
    
    # 兼容旧数据库：添加置顶字段
    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN is_pinned INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # 字段已存在
    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN pinned_at TEXT")
    except sqlite3.OperationalError:
        pass  # 字段已存在
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM notes")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"警告：数据库中已有 {count} 条记录，跳过迁移")
        conn.close()
        input("按回车键退出...")
        return
    
    # 迁移数据
    print("正在迁移数据...")
    migrated_count = 0
    for note in notes:
        try:
            cursor.execute('''
                INSERT INTO notes (title, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (
                note.get("title", ""),
                note.get("content", ""),
                note.get("created_at", datetime.now().isoformat()),
                note.get("updated_at", datetime.now().isoformat())
            ))
            migrated_count += 1
        except Exception as e:
            print(f"迁移笔记失败: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n迁移完成！成功迁移 {migrated_count} 条笔记")
    print(f"数据库文件: {db_path}")
    
    # 询问是否删除原 JSON 文件
    response = input("是否删除原 JSON 文件 (y/N)? ").strip().lower()
    if response == 'y':
        os.remove(json_path)
        print("已删除 notes_data.json")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()