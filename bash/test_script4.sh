#!/bin/bash
# Скрипт для правки конфигурациооного файла юнита и перемещения рабочей директории

set -e

echo "Поиск юнитов systemd по маске 'foobar-*'..."

# Поиск сервисов
units=$(systemctl list-unit-files --type=service --no-legend | grep -o 'foobar-[^.]*' | sort -u)

if [[ -z "$units" ]]; then
    echo "Не найдено юнитов по маске 'foobar-*'"
    exit 0
fi

echo "Найдены юниты: $units"

mv_dir="/srv/data/"

for unit in $units; do
    echo "Обработка: $unit"

    # Останавливаем сервис
    systemctl stop "$unit" 2>/dev/null || echo "Сервис $unit не был активен"

    # Извлекаем суффикс имени
    name_suffix="${unit#foobar-}"
    service_file="/etc/systemd/system/${unit}.service"

    # Модифицируем файл с помощью sed
    sed -i \
        -e "s|^ExecStart=.*|ExecStart=$mv_dir${name_suffix}/foobar-daemon infinity|" \
        -e "s|^WorkingDirectory=.*|WorkingDirectory=$mv_dir${name_suffix}|" \
        "$service_file"

    echo "Файл $service_file модифицирован"

	# Копируем рабочий репозиторий
	mv /opt/misc/$name_suffix $mv_dir
	echo "Переместили /opt/misc/$name_suffix в $mv_dir"

	# Перезагружаем systemd
	systemctl daemon-reload
	echo "Демон systemd перезагружен"

	# Запускаем сервис
	systemctl start "$unit"
	echo "Запустили сервис $unit"
done

echo "Обработка завершена!"
