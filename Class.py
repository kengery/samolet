# Базовая сцена: события, обновление, отрисовка.
class Scene:
    # Запоминает движок, чтобы сцена могла переключать экраны.
    def __init__(self, gameEngine):
        self.gameEngine = gameEngine  # игровой движок

    # Обрабатывает клики и клавиши. В базовом классе пусто.
    def handle_events(self, events):
        pass

    # Обновляет логику кадра. В базовом классе пусто.
    def update(self):
        pass

    # Рисует сцену. В базовом классе пусто.
    def render(self):
        pass
