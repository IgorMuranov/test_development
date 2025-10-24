import requests
import time
from datetime import datetime, timedelta, timezone
import json



def get_url(url):
    # Выполняем get запрос
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.RequestException as error:
        print(f"Ошибка запроса: {error}")
        exit(1)

    except KeyError as error:
        print(f"Ошибка парсинга ответа: {error}")
        exit(1)

def human_readable_view(data):
    timestamp_ms = data['time']
    timestamp_sec = timestamp_ms / 1000
    # Интерпретируем как UTC, так как API возвращает unix-epoch в мс
    human_time = datetime.utcfromtimestamp(timestamp_sec).replace(tzinfo=timezone.utc)

    # Пытаемся получить название временной зоны из ответа, иначе используем UTC/смещение
    tz_name = (
        data.get('tz_name')
        or (data.get('tzinfo') or {}).get('name')
        or data.get('tz')
    )
    if not tz_name:
        # Если в ответе нет названия TZ, показываем UTC
        # Попутно пытаемся отобразить смещение, если есть поле offset (в секундах)
        offset_seconds = data.get('offset')
        if isinstance(offset_seconds, (int, float)):
            sign = '+' if offset_seconds >= 0 else '-'
            hh = int(abs(offset_seconds)) // 3600
            mm = (int(abs(offset_seconds)) % 3600) // 60
            tz_name = f'UTC{sign}{hh:02d}:{mm:02d}'
        else:
            tz_name = 'UTC'

    return human_time, tz_name


def calculate_delta(url):
    # Фиксируем локальное текущее время в UTC, чтобы корректно сравнивать с серверным временем
    start_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    data = get_url(url)
    # Серверное время трактуем как UTC
    server_time = datetime.utcfromtimestamp(data['time'] / 1000).replace(tzinfo=timezone.utc)
    time_delta = server_time - start_time
    return time_delta


def run_range(url, quantity):
    # Выполняем серию запросов = quantity
    deltas = []
    for num in range(int(quantity)):
        time_delta = calculate_delta(url)
        deltas.append(time_delta.total_seconds())
        time.sleep(1)
    if deltas:
        avg_delta = sum(deltas) / len(deltas)
        return avg_delta


if __name__ == "__main__":
    # Задаем стартовые переменные
    url = "https://yandex.com/time/sync.json?geo=213"
    quentity = 5


    data = get_url(url)
    print('a)', f'выводим данные сайта {url} в сыром виде:\n {data}\n')

    human_time, tz_name = human_readable_view(data)
    print('b)', 'Выводим время в понятном формате', '\nвремя:', human_time, '\nчасовой пояс:', tz_name)

    time_delta = calculate_delta(url)
    print('c)', 'Выводим дельту', time_delta)


    avg_delta = run_range(url, quentity)
    print(f'd) Выводим среднюю дельту за {quentity} запросов: {avg_delta:.3f} сек')