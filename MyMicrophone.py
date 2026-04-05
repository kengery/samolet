import re
import threading


# Имя самолёта — ровно 2 слова: «имя» «номер», напр. «Рейс 3»
_PLANE_2 = r"(\S+)\s+(\S+)"
_TURN_RE = re.compile(
    rf"^\s*{_PLANE_2}\s+поворот\s+(влево|вправо)\s+(\d+(?:[.,]\d+)?)\s*$",
    re.IGNORECASE | re.UNICODE,
)
_SPEED_RE = re.compile(
    rf"^\s*{_PLANE_2}\s+скорость\s+(больше|меньше)\s+(\d+(?:[.,]\d+)?)\s*$",
    re.IGNORECASE | re.UNICODE,
)


def _norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def _norm_name_compact(s: str) -> str:
    """То же имя без пробелов — для совпадения «Рейс 3» и «Рейс3» в airplane.name."""
    return re.sub(r"\s+", "", _norm_name(s))


def _parse_num(s: str) -> float:
    return float(s.replace(",", "."))


def parse_command_text(text: str):
    """
    Разбор распознанной строки. Имя самолёта — два слова (напр. «Рейс 3»), как в airplane.name.
    Возвращает dict с ключами type ('turn'|'speed'), name, value — или None.
    """
    t = text.strip()
    if not t:
        return None
    m = _TURN_RE.match(t)
    if m:
        w1, w2, side, num_s = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
        plane_name = f"{w1.strip()} {w2.strip()}"
        n = _parse_num(num_s)
        if side == "влево":
            return {"type": "turn", "name": plane_name, "value": -abs(n)}
        return {"type": "turn", "name": plane_name, "value": abs(n)}
    m = _SPEED_RE.match(t)
    if m:
        w1, w2, how, num_s = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
        plane_name = f"{w1.strip()} {w2.strip()}"
        n = _parse_num(num_s)
        if how == "больше":
            return {"type": "speed", "name": plane_name, "value": abs(n)}
        return {"type": "speed", "name": plane_name, "value": -abs(n)}
    return None


class MyMicrophone:
    """Запись с микрофона и распознавание речи в фоне; очередь команд для сцены."""

    @staticmethod
    def same_plane_name(stored: str, spoken: str) -> bool:
        a, b = _norm_name(stored), _norm_name(spoken)
        if a == b:
            return True
        return _norm_name_compact(stored) == _norm_name_compact(spoken)

    _CHUNK = 1024

    def __init__(self):
        self._lock = threading.Lock()
        self._commands = []
        self._busy = False
        self._hold = threading.Event()
        self._calibrated = False

    def space_pressed(self):
        """Начать запись (вызывать при нажатии пробела)."""
        with self._lock:
            if self._busy:
                return
            self._busy = True
        self._hold.set()
        threading.Thread(target=self._record_while_held_thread, daemon=True).start()

    def space_released(self):
        """Закончить запись (вызывать при отпускании пробела)."""
        self._hold.clear()

    def start_recording_async(self):
        """Совместимость: то же, что space_pressed."""
        self.space_pressed()

    def _record_while_held_thread(self):
        try:
            import speech_recognition as sr
        except ImportError:
            print("Установите пакеты: pip install SpeechRecognition pyaudio")
            with self._lock:
                self._busy = False
            return
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                if not self._calibrated:
                    r.adjust_for_ambient_noise(source, duration=0.35)
                    self._calibrated = True
                chunks = []
                stream = source.stream
                while True:
                    chunk = stream.read(self._CHUNK)
                    chunks.append(chunk)
                    if not self._hold.is_set():
                        break
                raw = b"".join(chunks)
                if len(raw) < source.SAMPLE_WIDTH * 800:
                    print("(слишком короткая запись)")
                    return
                audio = sr.AudioData(
                    raw, source.SAMPLE_RATE, source.SAMPLE_WIDTH
                )
                text = r.recognize_google(audio, language="ru-RU")
                print(text)
                cmd = parse_command_text(text)
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

    def pop_command(self):
        """Забрать одну команду из очереди или None."""
        with self._lock:
            if self._commands:
                return self._commands.pop(0)
        return None

    def is_busy(self):
        with self._lock:
            return self._busy
