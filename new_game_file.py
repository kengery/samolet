import Tyrbylentnost
import Pogoda
import airplane
import Zona
from dataclasses import dataclass, field, asdict
import json
from typing import List

@dataclass
# Данные карты: самолёты, зоны, аэропорт. Читается из JSON.
class new_game_file:
    airplanes: List[airplane]  # список самолётов уровня
    tyrbylentnosts: List[Tyrbylentnost]  # зоны турбулентности
    zona: List[Zona]  # запретные многоугольники
    finish_x: int  # центр аэропорта по X
    finish_y: int  # центр аэропорта по Y
    finish_rx: int  # половина ширины картинки аэропорта
    finish_ry: int  # половина высоты картинки аэропорта
    # Сохраняет состав карты в поля объекта.
    def __init__(self, airplanes :list[airplane], tyrbylentnosts :list[Tyrbylentnost], zona: list[Zona], finish_x :int, finish_y : int, finish_rx :int, finish_ry :int ):
        self.airplanes=airplanes  # самолёты
        self.tyrbylentnosts=tyrbylentnosts  # турбулентности
        self.zona=zona  # запретные зоны

        self.finish_x=finish_x  # центр аэропорта X
        self.finish_y=finish_y  # центр аэропорта Y
        self.finish_rx=finish_rx  # половина ширины аэропорта
        self.finish_ry=finish_ry  # половина высоты аэропорта

    # Собирает поля карты в JSON-строку.
    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    # Собирает карту из JSON: самолёты, зоны и аэропорт.
    def from_json(cls, display, json_str: str) -> 'new_game_file':
        data = json.loads(json_str)  # словарь из файла уровня

        # Преобразуем вложенные словари обратно в объекты

        airplanes = [airplane.airplane(  # самолёты с карты
            x=plane['x'],
            y=plane['y'],
            dx=plane['dx'],
            dy=plane['dx'],
            display=display,
            file=plane['file'],
            name=plane['name'],
            speed=plane['speed'],
            speed_min=plane['speed_min'],
            speed_max=plane['speed_max'],
            angle=plane['angle'],
            benzin=plane['benzin'],
            visota_airplane=plane.get('visota_airplane', plane.get('altitude', 914)),
            visota_min=plane.get('visota_min', plane.get('altitude_min', 305)),
            visota_max=plane.get('visota_max', plane.get('altitude_max', 3048))) for plane in data['airplanes']]

        tyrbylentnosts = [Tyrbylentnost.Tyrbylentnost(  # зоны ветра
            x=plane['x'],
            y=plane['y'],
            dx=plane['dx'],
            dy=plane['dx'],
            display=display,
            file=plane['file'],
           ) for plane in data['tyrbylentnosts']]
        zona = [Zona.zona(  # запретные многоугольники
            points=plane['point'],
            color=plane['color'],
            display=display,
        ) for plane in data['zona']]

        return cls(
            airplanes=airplanes,
            tyrbylentnosts=tyrbylentnosts,
            zona=zona,
            finish_x=data['finish_x'],
            finish_y=data['finish_y'],
            finish_rx=data['finish_rx'],
            finish_ry=data['finish_ry']
        )
