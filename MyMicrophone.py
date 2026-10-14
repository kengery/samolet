import re
import threading


# Имя самолёта — ровно 2 слова: «имя» «номер», напр. «Рейс 3»
_PLANE_2 = r"(\S+)\s+(\S+)"  # шаблон двух слов имени рейса

_TURN_RE = re.compile(  # фраза «Рейс 3 поворот влево 1500»
    rf"^\s*{_PLANE_2}\s+поворот\s+(влево|вправо)\s+(\d+(?:[.,]\d+)?)\s*$",#это всё шаблон, а \s это строка
    re.IGNORECASE | re.UNICODE,
)
_SPEED_RE = re.compile(  # фраза «Рейс 3 скорость больше 100»
    rf"^\s*{_PLANE_2}\s+скорость\s+(больше|меньше)\s+(\d+(?:[.,]\d+)?)\s*$",
    re.IGNORECASE | re.UNICODE,
)


# Приводит имя к нижнему регистру и сжимает пробелы.
def _norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


# То же имя без пробелов — чтобы «Рейс 3» совпало с «Рейс3».
def _norm_name_compact(s: str) -> str:
    return re.sub(r"\s+", "", _norm_name(s))


# Число из фразы: запятая тоже считается десятичной.
def _parse_num(s: str) -> float:
    return float(s.replace(",", "."))


# Разбирает распознанную фразу в команду поворота или скорости, иначе None.
def parse_command_text(text: str):
    t = text.strip()  # фраза без крайних пробелов
    if not t:
        return None
    m = _TURN_RE.match(t)#текст который мы сказали сравниваем равен ли он нашему шаблону _TURN_RE
    if m:
        w1, w2, side, num_s = m.group(1), m.group(2), m.group(3).lower(), m.group(4)  # имя, сторона, число
        plane_name = f"{w1.strip()} {w2.strip()}"  # имя рейса двумя словами
        n = _parse_num(num_s)  # число из фразы
        if side == "влево":
            return {"type": "turn", "name": plane_name, "value": abs(n)}
        return {"type": "turn", "name": plane_name, "value": -abs(n)}
    m = _SPEED_RE.match(t)
    if m:
        w1, w2, how, num_s = m.group(1), m.group(2), m.group(3).lower(), m.group(4)  # имя, больше/меньше, число
        plane_name = f"{w1.strip()} {w2.strip()}"  # имя рейса двумя словами
        n = _parse_num(num_s)  # число из фразы
        if how == "больше":
            return {"type": "speed", "name": plane_name, "value": abs(n)}
        return {"type": "speed", "name": plane_name, "value": -abs(n)}
    return None


# Запись с микрофона и распознавание речи в фоне.
class MyMicrophone:
    @staticmethod
    # Сравнивает имя из JSON и сказанное имя («Рейс1» и «Рейс 3»).
    def same_plane_name(stored: str, spoken: str) -> bool:
        a, b = _norm_name(stored), _norm_name(spoken)  # имена с пробелами
        if a == b:
            return True
        return _norm_name_compact(stored) == _norm_name_compact(spoken)

    _CHUNK = 1024  # размер куска аудио при записи

    # Готовит очередь команд и флаги записи.
    def __init__(self):
        self._lock = threading.Lock()  # защита очереди и флагов
        self._commands = []  # распознанные команды
        self._busy = False  # идёт ли запись
        self._hold = threading.Event()  # пробел ещё зажат
        self._calibrated = False  # уже подстроились под шум

    # Начать запись (вызывать при нажатии пробела).
    def space_pressed(self):
        with self._lock:
            if self._busy:
                return
            self._busy = True
        self._hold.set()
        threading.Thread(target=self._record_while_held_thread, daemon=True).start()

    # Закончить запись (вызывать при отпускании пробела).
    def space_released(self):
        self._hold.clear()

    # То же, что space_pressed (старое имя).
    def start_recording_async(self):
        self.space_pressed()

    # Поток: пишет звук, пока зажат пробел, и распознаёт фразу.
    def _record_while_held_thread(self):
        try:
            import speech_recognition as sr
        except ImportError:
            print("Установите пакеты: pip install SpeechRecognition pyaudio")
            with self._lock:
                self._busy = False
            return
        try:
            r = sr.Recognizer()  # распознаватель Google Speech
            with sr.Microphone() as source:
                if not self._calibrated:
                    r.adjust_for_ambient_noise(source, duration=0.35)
                    self._calibrated = True
                chunks = []  # куски звука, пока зажат пробел
                stream = source.stream  # поток микрофона
                while True:
                    chunk = stream.read(self._CHUNK)  # очередной кусок аудио
                    chunks.append(chunk)
                    if not self._hold.is_set():
                        break
                raw = b"".join(chunks)  # вся запись целиком
                if len(raw) < source.SAMPLE_WIDTH * 800:
                    print("(слишком короткая запись)")
                    return
                audio = sr.AudioData(
                    raw, source.SAMPLE_RATE, source.SAMPLE_WIDTH
                )
                text = r.recognize_google(audio, language="ru-RU")  # распознанный текст
                print(text)
                cmd = parse_command_text(text)  # команда или None
                if cmd is not None:
                    with self._lock:
                        self._commands.append(cmd)
                else:
                    print(f"команда {text} не разознана")
        except sr.UnknownValueError:
            print("(речь не распознана)")
        except Exception as e:
            print(f"(ошибка микрофона: {e})")
        finally:
            with self._lock:
                self._busy = False

    # Забрать одну команду из очереди или None.
    def pop_command(self):
        with self._lock:
            if self._commands:
                return self._commands.pop(0)
        return None

    # True, если микрофон сейчас пишет.
    def is_busy(self):
        with self._lock:
            return self._busy
