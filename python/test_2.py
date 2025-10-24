import os, sys
import shutil
import json
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path


def clone_repo(repo_url, target_dir):
    #Клон репозитория в указанную директорию
    start = datetime.now()
    print(f"Клонируем репозиторий: {repo_url}")
    try:
        subprocess.run(['git', 'clone', repo_url, target_dir],
                       check=True, capture_output=True, text=True)
        print(f"Репозиторий клонирован за {datetime.now() - start}")
        return True
    except subprocess.CalledProcessError as error:
        print("Ошибка клонирования:")
        if error.stdout:
            print(error.stdout)
        if error.stderr:
            print(error.stderr)
        return False


def clean_root_except(root_dir, keep_relative_path):
    #Удалить все директории в корне, кроме первой части пути keep_relative_path
    start = datetime.now()
    first_keep_dir = Path(keep_relative_path).parts[0] if keep_relative_path else ""
    print(f"Удаляем директории в корне, кроме: {first_keep_dir or '<none>'}")

    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item not in (first_keep_dir, '.git'):
            shutil.rmtree(item_path)
            print(f"  - удалена директория: {item}")

    print(f"Очистка завершена за {datetime.now() - start}")


def list_source_files(source_dir):
    # Собрать список файлов (.py, .js, .sh) относительными путями от source_dir
    extensions = ('.py', '.js', '.sh')
    files = []
    for ext in extensions:
        for file_path in Path(source_dir).rglob(f'*{ext}'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(source_dir)))
    return sorted(files)


def write_version_json(source_dir, version):
    # Создать version.json в директории исходного кода
    start = datetime.now()
    files = list_source_files(source_dir)
    content = {"name": "hello world", "version": version, "files": files}
    out_path = os.path.join(source_dir, 'version.json')
    with open(out_path, 'w') as fh:
        json.dump(content, fh, indent=2)
    print(f"Создан {out_path} за {datetime.now() - start}")
    return out_path


def make_zip(source_dir, out_dir):
    # Создать zip-архив из source_dir в текущей директории с именем <lastdir><DDMMYYYY>.zip
    start = datetime.now()
    last_dir = os.path.basename(os.path.normpath(source_dir))
    date_suffix = datetime.now().strftime('%d%m%Y')
    archive_name = f"{last_dir}{date_suffix}"
    archive_path = os.path.join(out_dir, archive_name)
    shutil.make_archive(archive_path, 'zip', source_dir)
    print(f"Архив создан: {archive_path}.zip за {datetime.now() - start}")
    return f"{archive_name}.zip"


def run_build(repo_url, source_path, version):
    # Полный сценарий сборки по ТЗ
    total_start = datetime.now()
    print("Начинаем сборку...")
    with tempfile.TemporaryDirectory() as tmp:
        if not clone_repo(repo_url, tmp):
            return

        clean_root_except(tmp, source_path)

        full_source = os.path.join(tmp, source_path)
        if not os.path.exists(full_source):
            print(f"Директория исходного кода не найдена: {full_source}")
            return

        write_version_json(full_source, version)
        archive_name = make_zip(full_source, os.getcwd())
        print(f"Готово. Создан архив: {archive_name}")
    print(f"Полное время сборки: {datetime.now() - total_start}")


if __name__ == "__main__":
    """
    Пример запуска скрипта 
    py -3 script_2.py repo='https://github.com/paulbouwer/hello-kubernetes' path='src/app' ver='25.3000'
    """
    # Парсим переменные
    var = {}
    for arg in sys.argv[1:]:  # Пропускаем имя скрипта
        if '=' in arg:
            key, value = arg.split('=', 1)
            value = value.strip('"\'')  # Убираем кавычки
            var[key.strip()] = value

    run_build(var['repo'], var['path'], var['ver'])