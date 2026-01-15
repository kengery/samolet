import Tyrbylentnost
import Pogoda
import airplane
from dataclasses import dataclass, field, asdict
import json
from typing import List

@dataclass
class new_game_file:
    airplanes: List[airplane]
    tyrbylentnosts: List[Tyrbylentnost]
    pogoda: List[Pogoda]
    finish_x: int
    finish_y: int
    finish_rx: int
    finish_ry: int
    def __init__(self, airplanes :list[airplane], tyrbylentnosts :list[Tyrbylentnost],pogoda: List[Pogoda], finish_x :int, finish_y : int, finish_rx :int, finish_ry :int ):
        self.airplanes=airplanes
        self.tyrbylentnosts=tyrbylentnosts
        self.pogoda=pogoda

        self.finish_x=finish_x
        self.finish_y=finish_y
        self.finish_rx=finish_rx
        self.finish_ry=finish_ry

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """Сериализация в JSON"""
        return json.dumps(asdict(self), indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def from_json(cls, display, json_str: str) -> 'new_game_file':
        """Десериализация из JSON"""
        data = json.loads(json_str)

        # Преобразуем вложенные словари обратно в объекты

        airplanes = [airplane.airplane(
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
            benzin=plane['benzin']) for plane in data['airplanes']]

        tyrbylentnosts = [Tyrbylentnost.Tyrbylentnost(
            x=plane['x'],
            y=plane['y'],
            dx=plane['dx'],
            dy=plane['dx'],
            display=display,
            file=plane['file'],
           ) for plane in data['tyrbylentnosts']]
        pogoda = [Pogoda.Pogoda(
            x=plane['x'],
            y=plane['y'],
            dx=plane['dx'],
            dy=plane['dx'],
            display=display,
            file=plane['file'],
        ) for plane in data['pogoda']]

        return cls(
            airplanes=airplanes,
            tyrbylentnosts=tyrbylentnosts,
            pogoda=pogoda,
            finish_x=data['finish_x'],
            finish_y=data['finish_y'],
            finish_rx=data['finish_rx'],
            finish_ry=data['finish_ry']
        )