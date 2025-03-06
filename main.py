"""
main.py

Запускает FastAPI-приложение, которое:
 - Определяет корневую папку (ROOT_DIR) как родительскую от текущего файла (myproject).
 - Предоставляет 2 эндпоинта:
   1) /list-project          - список файлов/папок в проекте (рекурсивно)
   2) /read-file?filepath=   - прочитать содержимое конкретного файла
 - Папку gpt_plugin по умолчанию пропускаем при обходе (чтобы плагин сам себя не читал).

Как запускать:
  cd myproject/gpt_plugin
  pip install fastapi uvicorn
  uvicorn main:app --host 0.0.0.0 --port 3333

Далее откройте http://localhost:3333/docs для просмотра эндпоинтов.
Если нужен HTTPS и публичный доступ, используйте ngrok:
  ngrok http 3333
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from typing import List, Optional

app = FastAPI(
    title="Local Read-Only Plugin",
    description="Плагин для чтения структуры и файлов проекта (без записи).",
    version="0.1.0",
)

# Определяем корень проекта (на уровень выше текущего файла)
ROOT_DIR = Path(__file__).parent.parent.resolve()

# Монтируем статику, чтобы отдавать openapi.yaml и ai-plugin.json
# Теперь при обращении к /static/openapi.yaml или /static/ai-plugin.json
# файлы будут раздаваться напрямую из папки gpt_plugin
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent)), name="static")


@app.get("/list-project")
def list_project(subdir: Optional[str] = None) -> List[dict]:
    """
    Рекурсивно обходит файлы/папки, начиная с ROOT_DIR/subdir (или ROOT_DIR, если subdir не указан).
    Возвращает список словарей вида:
       {
         'path': 'src/utils.py',
         'is_dir': False
       }
    Папку 'gpt_plugin' пропускает.
    Параметр subdir может указывать на вложенную папку, например 'src' или 'src/'.
    """

    if subdir:
        base_path = ROOT_DIR / subdir
    else:
        base_path = ROOT_DIR

    if not base_path.exists():
        raise HTTPException(status_code=404, detail=f"Указанный путь {base_path} не существует.")

    results = []

    for dirpath, dirnames, filenames in os.walk(base_path):
        # Пропускаем саму папку gpt_plugin
        if "gpt_plugin" in dirpath:
            continue

        for d in dirnames:
            full_path = Path(dirpath) / d
            rel_path = full_path.relative_to(ROOT_DIR)
            results.append({
                "path": str(rel_path),
                "is_dir": True
            })
        for f in filenames:
            full_path = Path(dirpath) / f
            rel_path = full_path.relative_to(ROOT_DIR)
            results.append({
                "path": str(rel_path),
                "is_dir": False
            })

    return results


@app.get("/read-file")
def read_file(filepath: str = Query(..., description="Относительный путь к файлу внутри проекта")):
    """
    Возвращает содержимое файла, если он существует и не находится в папке gpt_plugin.
    filepath - относительный путь к файлу внутри проекта, например: 'src/utils.py'.
    """
    target_path = (ROOT_DIR / filepath).resolve()

    # Проверим, что запрошенный путь лежит внутри проекта
    if not str(target_path).startswith(str(ROOT_DIR)):
        raise HTTPException(status_code=403, detail="Запрошенный файл вне корня проекта.")

    # Проверим, что не заходим в папку gpt_plugin
    if "gpt_plugin" in target_path.parts:
        raise HTTPException(status_code=403, detail="Доступ к файлам плагина запрещён.")

    # Проверим, что файл существует
    if not target_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден.")

    # Считаем содержимое
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {e}")

    return {
        "filepath": filepath,
        "content": content
    }
