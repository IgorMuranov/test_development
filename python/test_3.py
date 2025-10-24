import re
import sys
import json
from packaging import version

# Функция генерации двух версий по шаблону
# Символ * заменяется двумя разными цифрами (например, 9 и 3)
def generate_versions_from_template(template):
    parts = template.split('.')
    versions = []
    for v1 in [9, 3]:  # два варианта подстановки вместо '*'
        new_parts = [str(v1) if p == '*' else p for p in parts]
        versions.append('.'.join(new_parts))
    return versions

# Основная функция обработки версий
# base_version - версия для сравнения (строка)
# config - словарь с шаблонами {имя: шаблон}
def process_versions(base_version, config):
    all_versions = []
    # Генерируем версии для каждого шаблона
    for key, template in config.items():
        generated_versions = generate_versions_from_template(template)
        all_versions.extend(generated_versions)
    # Сортируем все версии
    all_versions = sorted(all_versions, key=version.parse)
    # Фильтруем версии, которые меньше base_version
    filtered = [v for v in all_versions if version.parse(v) < version.parse(base_version)]
    return all_versions, filtered
if __name__ == "__main__":
    """
    Пример запуска скрипта 
    py -3 script_3.py ver='3.7.5' config_file='config1.json'
    """
    # Парсим переменные
    var = {}
    for arg in sys.argv[1:]:  # Пропускаем имя скрипта
        if '=' in arg:
            key, value = arg.split('=', 1)
            value = value.strip('"\'')  # Убираем кавычки
            var[key.strip()] = value

    with open(var['config_file'], 'r') as config_file:
        config = json.load(config_file)

    all_versions, filtered = process_versions(var['ver'], config)

    print("Все сгенерированные версии (отсортированные):")
    print(all_versions)
    print("Версии старше базовой (меньше):")
    print(filtered)