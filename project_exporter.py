import os
import re

# Настройки
PROJECT_ROOT = "."  # Папка, где лежит скрипт
OUTPUT_FILE = "project_snapshot.txt"
INCLUDE_PATTERNS = [r"\.py$", r"\.html$", r"\.js$", r"\.css$", r"\.env$", r"Procfile$"]
EXCLUDE_DIRS = [
    "__pycache__", 
    "node_modules", 
    ".git", 
    ".venv", 
    "venv", 
    "env", 
    ".env",
    "migrations",
    "tests",
    "docs"
]

def should_include(path):
    return any(re.search(pattern, path) for pattern in INCLUDE_PATTERNS)

def build_tree(root):
    tree = []
    for root_dir, dirs, files in os.walk(root):
        # Исключаем папки
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Убираем корень из отображаемого пути
        rel_dir = os.path.relpath(root_dir, root)
        if rel_dir == ".":
            rel_dir = os.path.basename(os.path.abspath(root))

        depth = rel_dir.count(os.sep)
        indent = "│   " * depth
        subdir = os.path.basename(rel_dir)
        tree.append(f"{indent}├── {subdir}/")

        # Файлы
        for file in sorted(files):
            if should_include(file):
                file_path = os.path.join(rel_dir, file)
                rel_path = os.path.relpath(file_path, root)
                tree.append(f"{indent}│   ├── {file}")

    # Убираем первый "├── имя_проекта/"
    if tree:
        tree[0] = tree[0].replace("├── ", "└── ", 1)
    return "\n".join(tree)

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Не удалось прочитать файл: {e}"

def export_project():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        # Структура
        out.write("# 🗂 СТРУКТУРА ПРОЕКТА\n")
        tree = build_tree(PROJECT_ROOT)
        out.write(tree.strip() + "\n\n")

        # Файлы
        file_count = 0
        for root_dir, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in sorted(files):
                filepath = os.path.join(root_dir, file)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                if should_include(rel_path):
                    out.write(f"# 📄 ФАЙЛ: {rel_path}\n")
                    content = read_file(filepath)
                    out.write(f"```{rel_path.split('.')[-1]}\n")
                    out.write(content + "\n")
                    out.write("```\n\n")
                    file_count += 1

        out.write(f"# ✅ Экспорт завершён. Включено файлов: {file_count}\n")
    
    print(f"✅ Проект экспортирован в {OUTPUT_FILE}")
    print(f"📁 Включено файлов: {file_count}")

if __name__ == "__main__":
    export_project()