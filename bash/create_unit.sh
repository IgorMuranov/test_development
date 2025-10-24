#!/bin/bash
# Скрипт для создания юнита
# Имя юнита = foobar-$1

set -e

service_file="/etc/systemd/system/foobar-$1.service"
work_dir="/opt/misc/$1"

#Копируем шаблон файла конфигурации
cp ./foobar-name_unit.service $service_file
echo "Создали файл конфигурации $service_file"

# Модифицируем файл с помощью sed
sed -i \
    -e "s|^ExecStart=.*|ExecStart=/opt/misc/$1/foobar-daemon infinity|" \
    -e "s|^WorkingDirectory=.*|WorkingDirectory=/opt/misc/$1|" \
    "$service_file"

echo "Файл $service_file модифицирован"

# Создаем рабочую директорию
mkdir -p $work_dir
echo "Создали рабочую директорию $work_dir"

# "Копируем исполняемый файл"
cp ./foobar-daemon $work_dir
echo "Скопировали исполняемый файл в $work_dir"

# Перезагружаем systemd
systemctl daemon-reload
echo "Демон systemd перезагружен"

# Запускаем сервис
systemctl enable foobar-$1
systemctl start foobar-$1
echo "Запустили сервис foobar-$1"

echo "Завершили создание юнита foobar-$1"