import speech_recognition as sr
import time
import queue
import numpy as np
import threading

# Очередь для передачи команд
command_queue = queue.Queue()
# Глобальные флаги для управления потоком
running_speech = True

def speech_recognizer_thread():
    """Оптимизированный поток для распознавания речи"""
    recognizer = sr.Recognizer()

    # Оптимизация: используем более низкий уровень шума и timeout
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.5

    # Инициализация микрофона один раз
    try:
        microphone = sr.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
    except Exception as e:
        print(f"Ошибка инициализации микрофона: {e}")
        return

    print("Голосовое управление запущено...")

    while running_speech:
        try:
            # Используем listen с меньшим timeout для быстрой реакции
            with microphone as source:
                audio = recognizer.listen(
                    source,
                    timeout=0.5,  # Уменьшен timeout
                    phrase_time_limit=2  # Уменьшен лимит фразы
                )

            # Быстрое распознавание с обработкой в отдельном потоке
            def recognize():
                try:
                    text = recognizer.recognize_google(
                        audio,
                        language='ru-RU',
                        show_all=False  # Ускоряет распознавание
                    ).lower()

                    # Быстрая обработка ключевых слов
                    if 'право' in text or 'правой' in text:
                        command_queue.put(('turn', 'право', 5))
                    elif 'влево' in text or 'лево' in text or 'левой' in text:
                        command_queue.put(('turn', 'влево', 5))
                    print(f"{text}")

                except Exception as e:
                    pass  # Игнорируем ошибки распознавания

            # Запускаем распознавание в отдельном потоке чтобы не блокировать захват аудио
            threading.Thread(target=recognize, daemon=True).start()

        except sr.WaitTimeoutError:
            continue  # Просто продолжаем слушать
        except Exception as e:
            # Не печатаем каждую ошибку чтобы не замедлять
            time.sleep(0.01)

def vabor(click_airplane):
    try:
        # Берем только одну команду за раз чтобы не блокировать
        while True:  # Обрабатываем все команды в очереди
            command = command_queue.get_nowait()
            cmd_type, direction, value = command
            if cmd_type == 'turn':
                if direction == 'право':
                    print("Выполняю поворот вправо")
                    if click_airplane is not None:
                        click_airplane.add_angle(-20)
                elif direction == 'влево':
                    print("Выполняю поворот влево")
                    if click_airplane is not None:
                        click_airplane.add_angle(20)

    except queue.Empty:
        pass  # Нет команд в очереди
    except Exception as e:
        print(f"Ошибка обработки команды: {e}")